from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from sqlalchemy.sql import func


# -------------------- Flask Setup --------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yoursecretkey'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'local_services.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# -------------------- Database Models --------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='customer')  # customer/provider/admin
    location = db.Column(db.String(100))

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    provider = db.relationship('User', backref='services')

    @property
    def avg_rating(self):
        avg = db.session.query(func.avg(Booking.rating)).filter(
            Booking.service_id == self.id,
            Booking.rating > 0
        ).scalar()
        return round(avg, 1) if avg else 0

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    status = db.Column(db.String(50), default='Pending')
    rating = db.Column(db.Integer, default=0)  # ⭐ NEW FIELD (0 means not rated yet)


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text, nullable=False)
    sender_role = db.Column(db.String(20))  # 'customer' or 'provider'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- Routes --------------------

@app.route('/')
def index():
    services = Service.query.filter_by(is_available=True).all()
    return render_template('index.html', services=services)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        role = request.form['role']
        location = request.form.get('location')

        new_user = User(username=username, email=email, password=password, role=role, location=location)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

        login_user(user)
        flash('Logged in successfully!', 'success')

        # ✅ Redirect based on role
        if user.role == "admin":
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

# ----------- Service Management ------------

@app.route('/create_service', methods=['GET', 'POST'])
@login_required
def create_service():
    if current_user.role != 'provider':
        flash('Only service providers can create services.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        location = request.form['location']

        new_service = Service(provider_id=current_user.id, name=name,
                              description=description, price=price, location=location)
        db.session.add(new_service)
        db.session.commit()
        flash('Service created successfully!', 'success')
        return redirect(url_for('services'))

    return render_template('create_service.html')

@app.route('/services')
def services():
    query = request.args.get('q', '')
    location = request.args.get('location', '')

    services = Service.query.filter(Service.is_available == True)
    if query:
        services = services.filter(Service.name.contains(query))
    if location:
        services = services.filter(Service.location.contains(location))

    services = services.all()  # ✅ Just fetch directly, no manual avg_rating assignment
    return render_template('services.html', services=services)


@app.route('/hire/<int:service_id>')
@login_required
def hire(service_id):
    service = Service.query.get_or_404(service_id)
    new_booking = Booking(customer_id=current_user.id, provider_id=service.provider_id, service_id=service.id, status="Hired")
    db.session.add(new_booking)
    db.session.commit()
    # flash(f'You hired {service.name}! Chat is now enabled.', 'success')
    return redirect(url_for('rate_service', booking_id=new_booking.id))

# ----------- Chat System ------------

@app.route('/chat/<int:provider_id>', methods=['GET', 'POST'])
@login_required
def chat(provider_id):
    if request.method == 'POST':
        msg = request.form['message']
        chat_msg = Chat(customer_id=current_user.id, provider_id=provider_id,
                        message=msg, sender_role=current_user.role)
        db.session.add(chat_msg)
        db.session.commit()

    chats = Chat.query.filter_by(provider_id=provider_id).order_by(Chat.timestamp.asc()).all()
    provider = User.query.get(provider_id)
    return render_template('chat.html', chats=chats, provider=provider)

@app.route('/rate/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def rate_service(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.customer_id != current_user.id:
        flash("You can only rate your own bookings.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        rating = int(request.form['rating'])
        if 1 <= rating <= 5:
            booking.rating = rating
            db.session.commit()
            flash("Thank you for rating!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid rating.", "danger")

    return render_template('rate_service.html', booking=booking)


# ----------- Admin Dashboard ------------

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Admin access only.', 'danger')
        return redirect(url_for('index'))

    providers = User.query.filter_by(role='provider').all()
    customers = User.query.filter_by(role='customer').all()
    active_services = Service.query.filter_by(is_available=True).all()
    bookings = Booking.query.all()

    return render_template('admin_dashboard.html',
                           providers=providers,
                           customers=customers,
                           active_services=active_services,
                           bookings=bookings)


# -------------------- Run & Auto Admin Creation --------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # ✅ Auto-create admin if not exists
        if not User.query.filter_by(role='admin').first():
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password=generate_password_hash("admin123", method='pbkdf2:sha256'),
                role="admin"
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Default admin created: Email: admin@example.com | Password: admin123")

    app.run(debug=True)
