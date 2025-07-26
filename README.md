# Local Link

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

<img width="1348" height="630" alt="image" src="https://github.com/user-attachments/assets/ff9dca56-14a1-4d29-bcac-73db07454bf5" />

<img width="1348" height="626" alt="image" src="https://github.com/user-attachments/assets/d1987558-a5c1-4356-8ae5-25c670714a26" />

<img width="1345" height="623" alt="image" src="https://github.com/user-attachments/assets/544cf1d0-b208-497c-9002-7e6656daf765" />

<img width="1349" height="631" alt="image" src="https://github.com/user-attachments/assets/95f93a09-d5f8-48f0-81c7-8dbd23610077" />

<img width="1343" height="627" alt="image" src="https://github.com/user-attachments/assets/8808618d-941a-49f1-8225-1864619e6836" />

---

## ⚙️ Installation & Setup

1. **Clone the repository**  
```bash
git clone https://github.com/vaibhavrawat27/local-link.git
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
