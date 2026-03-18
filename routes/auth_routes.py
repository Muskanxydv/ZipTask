from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
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

    # log user in and redirect to dashboard
    session["user_id"] = new_user.id
    return redirect(url_for("dashboard"))


# -----------------------------
# Login Page
# -----------------------------
@auth_bp.route("/login")
def login_page():

    return render_template("login_page.html")

# -----------------------------
# Handle Login
# -----------------------------
@auth_bp.route("/login-user", methods=["POST"])
def login_user():

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        flash("Invalid email or password")
        return redirect(url_for("auth.login_page"))

    session["user_id"] = user.id
    return redirect(url_for("dashboard"))

# -----------------------------
# Handle Logout
# -----------------------------
@auth_bp.route("/logout")
def logout():

    session.pop("user_id", None)
    return redirect(url_for("home"))
