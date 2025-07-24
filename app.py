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
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    address = db.Column(db.String(200))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    payment_method = db.Column(db.String(20))
    rating = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="Pending")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ Relationships
    service = db.relationship('Service', backref='bookings', lazy=True)
    customer = db.relationship('User', foreign_keys=[customer_id], backref='customer_bookings', lazy=True)
    provider = db.relationship('User', foreign_keys=[provider_id], backref='provider_bookings', lazy=True)



class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    complaint_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="Pending")  # Pending/Resolved
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="complaints")


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

@app.context_processor
def inject_provider_notifications():
    """Make provider's pending notification count available globally in templates"""
    pending_count = 0
    if current_user.is_authenticated and current_user.role == "provider":
        pending_count = Booking.query.filter_by(provider_id=current_user.id, status="Pending").count()
    return dict(provider_pending_count=pending_count)


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


@app.route('/submit_complaint', methods=['POST'])
@login_required
def submit_complaint():
    message = request.form['message']
    new_complaint = Complaint(user_id=current_user.id, message=message)
    db.session.add(new_complaint)
    db.session.commit()
    flash("Your complaint has been submitted successfully!", "success")
    return redirect(request.referrer or url_for('index'))


# ----------- Chat System ------------
@app.route('/complaint', methods=['GET', 'POST'])
@login_required
def complaint():
    if request.method == 'POST':
        complaint_text = request.form['complaint_text']
        if complaint_text.strip():
            new_complaint = Complaint(user_id=current_user.id, complaint_text=complaint_text)
            db.session.add(new_complaint)
            db.session.commit()
            flash("Your complaint has been submitted successfully.", "success")
        else:
            flash("Complaint cannot be empty.", "danger")

    my_complaints = Complaint.query.filter_by(user_id=current_user.id).order_by(Complaint.timestamp.desc()).all()
    return render_template('complaint.html', my_complaints=my_complaints)

@app.route('/customer/notifications')
@login_required
def customer_notifications():
    if current_user.role != 'customer':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('index'))

    notifications = Booking.query.filter_by(customer_id=current_user.id).order_by(Booking.timestamp.desc()).all()
    return render_template('customer_notifications.html', notifications=notifications)

@app.route('/provider/notifications')
@login_required
def provider_notifications():
    if current_user.role != "provider":
        flash("Access Denied", "danger")
        return redirect(url_for('index'))

    bookings = Booking.query.filter_by(provider_id=current_user.id).order_by(Booking.timestamp.desc()).all()
    return render_template('provider_notifications.html', bookings=bookings)

@app.route('/booking/<int:booking_id>/<action>')
@login_required
def update_booking_status(booking_id, action):
    booking = Booking.query.get_or_404(booking_id)
    if current_user.id != booking.provider_id:
        flash("Unauthorized!", "danger")
        return redirect(url_for('index'))

    if action == "accept":
        booking.status = "Accepted"
    elif action == "reject":
        booking.status = "Rejected"
    db.session.commit()
    flash("Booking status updated!", "success")
    return redirect(url_for('provider_notifications'))

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

@app.route('/book/<int:service_id>', methods=['GET', 'POST'])
@login_required
def book(service_id):
    service = Service.query.get_or_404(service_id)
    provider_id = service.provider_id

    if request.method == 'POST':
        booking = Booking(
            customer_id=current_user.id,
            provider_id=provider_id,
            service_id=service.id,
            customer_name=request.form['customer_name'],
            age=request.form['age'],
            gender=request.form['gender'],
            address=request.form['address'],
            date=request.form['date'],
            time=request.form['time'],
            payment_method=request.form['payment_method'],
            status="Pending"
        )
        db.session.add(booking)
        db.session.commit()
        flash("Booking request sent to provider!", "success")
        return redirect(url_for('customer_notifications'))

    return render_template('booking_form.html', service=service)

# ----------- Admin Dashboard ------------

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Admin access only.', 'danger')
        return redirect(url_for('index'))

    providers = User.query.filter_by(role="provider").all()
    customers = User.query.filter_by(role="customer").all()
    active_services = Service.query.filter_by(is_available=True).all()
    bookings = Booking.query.all()
    complaints = Complaint.query.order_by(Complaint.timestamp.desc()).all()

    return render_template(
        'admin_dashboard.html',
        providers=providers,
        customers=customers,
        active_services=active_services,
        bookings=bookings,
        complaints=complaints
    )

# ✅ Delete Provider
@app.route('/admin/delete_provider/<int:provider_id>')
@login_required
def delete_provider(provider_id):
    if current_user.role == "admin":
        provider = User.query.get_or_404(provider_id)
        db.session.delete(provider)
        db.session.commit()
        flash("Provider account deleted!", "success")
    return redirect(url_for('admin'))

# ✅ Delete Customer
@app.route('/admin/delete_customer/<int:customer_id>')
@login_required
def delete_customer(customer_id):
    if current_user.role == "admin":
        customer = User.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        flash("Customer account deleted!", "success")
    return redirect(url_for('admin'))

# ✅ Delete Service
@app.route('/admin/delete_service/<int:service_id>')
@login_required
def delete_service(service_id):
    if current_user.role == "admin":
        service = Service.query.get_or_404(service_id)
        db.session.delete(service)
        db.session.commit()
        flash("Service deleted successfully!", "success")
    return redirect(url_for('admin'))

# ✅ Mark Complaint Resolved
@app.route('/admin/resolve_complaint/<int:complaint_id>')
@login_required
def resolve_complaint(complaint_id):
    if current_user.role == "admin":
        complaint = Complaint.query.get_or_404(complaint_id)
        complaint.status = "Resolved"
        db.session.commit()
        flash("Complaint marked as resolved!", "success")
    return redirect(url_for('admin'))


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
