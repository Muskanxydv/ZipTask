from flask import Blueprint, jsonify, request, redirect, url_for, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models import db
import smtplib
import random
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

auth_bp = Blueprint("auth", __name__)

SENDER_EMAIL = os.environ.get("MAIL_USERNAME")
SENDER_PASSWORD = os.environ.get("MAIL_PASSWORD")

def send_otp_email(recipient_email, otp):
    msg = MIMEText(f"""Hii! 
                Welcome to ZipTask!
                Your 6-digit email verification code is: {otp}.
                Enter this code in the app to complete your registration.
                   
                Thanks,
                ZipTask Team""")
    msg['Subject'] = "ZipTask Account Verification!!"
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

@auth_bp.route("/register")
def register_page():
    return render_template("register.html")


@auth_bp.route("/register-user", methods=["POST"])
def register_user():
    data = request.json
    name = data.get("fullname")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"error": "This email is already registered."}), 400

    # Generate OTP & Save Temp Session
    otp = str(random.randint(100000, 999999))
    session['temp_user'] = {
        "name": name,
        "email": email,
        "phone": phone,
        "password": generate_password_hash(password)
    }
    session['otp'] = otp

    # Send the email
    email_sent = send_otp_email(email, otp)
    
    if email_sent:
        return jsonify({"message": "OTP sent successfully!"})
    else:
        return jsonify({"error": "Failed to send email. Please check your server console."}), 500


@auth_bp.route("/confirm-otp", methods=["POST"])
def confirm_otp():
    data = request.json
    user_entered_otp = data.get("otp")
    real_otp = session.get("otp")

    if user_entered_otp and user_entered_otp == real_otp:
        temp_user = session.get("temp_user")
        
        new_user = User(
            name=temp_user["name"],
            email=temp_user["email"],
            phone=temp_user["phone"],
            password=temp_user["password"]
        )

        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id  
        session.pop("temp_user", None)
        session.pop("otp", None)

        return jsonify({"redirect": url_for("dashboard.dashboard_page")})
    else:
        return jsonify({"error": "Incorrect code. Please try again."}), 400

@auth_bp.route("/login")
def login_page():
    return render_template("login_page.html")

@auth_bp.route("/login-user", methods=["POST"])
def login_user():
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()
    if not user:
        return render_template("login_page.html", email_error="This email doesn't exist.", email_input=email)
    if not check_password_hash(user.password, password):
        return render_template("login_page.html", password_error="Incorrect password.", email_input=email)
    session["user_id"] = user.id
    return redirect(url_for("dashboard.dashboard_page"))
