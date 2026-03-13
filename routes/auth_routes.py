from flask import Blueprint, request, redirect, url_for, render_template
from werkzeug.security import generate_password_hash
from models.user import User
from models import db

auth_bp = Blueprint("auth", __name__)


# -----------------------------
# Show Registration Page
# -----------------------------
@auth_bp.route("/register")
def register_page():

    return render_template("register.html")


# -----------------------------
# Handle Registration
# -----------------------------
@auth_bp.route("/register-user", methods=["POST"])
def register_user():

    name = request.form["fullname"]
    email = request.form["email"]
    phone = request.form["phone"]
    password = request.form["password"]

    # check if email already exists
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return "Email already registered"

    # hash password before storing
    hashed_password = generate_password_hash(password)

    # create new user object
    new_user = User(
        name=name,
        email=email,
        phone=phone,
        password=hashed_password
    )

    # save to database
    db.session.add(new_user)
    db.session.commit()

    # redirect user to dashboard after account creation
    return redirect(url_for("dashboard", user_id=new_user.id))


# -----------------------------
# Login Page
# -----------------------------
@auth_bp.route("/login")
def login_page():

    return render_template("login_page.html")
