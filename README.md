# Local Link

![Local Link Banner](screenshots/banner.png)

## 📌 Project Overview
**Local Link** is a local service provider platform designed to connect **service providers** with **customers** seamlessly.  
Built with **Flask, SQLAlchemy, and Flask-Login**, this project is ideal for **students, beginners, and learners** who want to understand how real-world service platforms are built.

This platform can be considered:
- ✅ A **mini-project** for academic purposes.
- ✅ A **major/advanced project** with proper features like booking, rating, and feedback systems.

---

## 🚀 Features
- **User Roles**: Customer, Service Provider, and Admin.
- **Service Listings**: Providers can create and manage services.
- **Booking System**: Customers can book services and track notifications.
- **Rating & Feedback**: Customers can rate services after booking.
- **Complaint System**: Users can submit and track complaints.
- **Chat System**: Real-time communication between customers and providers.
- **Location-Based Personalization**: Shows services near the user's location.
- **Admin Dashboard**: Manage users, services, and complaints.
- **Authentication**: Secure login and registration with password hashing.

---

## 🛠️ Tech Stack
- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Database**: SQLite
- **Frontend**: HTML, Bootstrap, Jinja2 Templates
- **Other**: Werkzeug (for password hashing)

---

## 📂 Project Structure
```
LocalLink/
├── app.py                # Main Flask application
├── local_services.db     # SQLite database
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── profile.html
│   ├── services.html
│   ├── booking_form.html
│   ├── complaint.html
│   └── admin_dashboard.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── screenshots/
│       ├── banner.png
│       ├── homepage.png
│       ├── profile_page.png
│       └── admin_dashboard.png
└── README.md
```

---

## 📸 Screenshots

### 1. Homepage
![Homepage](screenshots/homepage.png)

### 2. Profile Page
![Profile Page](screenshots/profile_page.png)

### 3. Admin Dashboard
![Admin Dashboard](screenshots/admin_dashboard.png)

---

## ⚙️ Installation & Setup

1. **Clone the repository**  
```bash
git clone https://github.com/your-username/local-link.git
cd local-link
```

2. **Create a virtual environment**  
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3. **Install dependencies**  
```bash
pip install -r requirements.txt
```

4. **Run the application**  
```bash
python app.py
```

5. **Access in Browser**  
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 👤 Default Admin Credentials
```
Email: admin@example.com
Password: admin123
```

---

## 🎯 Future Enhancements
- ✅ Payment Gateway Integration  
- ✅ Real-time Chat using WebSockets  
- ✅ Push Notifications  
- ✅ Advanced Search & Filtering  

---

## 📝 License
This project is open-source and available under the **MIT License**.

---

## 🙌 Contribution
Contributions, issues, and feature requests are welcome!  
Feel free to fork this repository and submit a pull request.

---

## ✨ Author
Developed by **Vaibhav Rawat**  
For learning and academic purposes.
