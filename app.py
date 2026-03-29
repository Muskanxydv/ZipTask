from flask import Flask, render_template
from models import db
from models.user import User
from models.task import Task
from routes.dashboard_routes import dashboard_bp
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from routes.auth_routes import auth_bp

app = Flask(__name__)
app.register_blueprint(dashboard_bp)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ziptask.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.environ.get("SECRET_KEY", "fallback_default_secret_key")

db.init_app(app)

app.register_blueprint(auth_bp)


# --------------------------
# Home Page
# --------------------------

@app.route("/")
def home():
    return render_template("home_page.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot_password.html")



# --------------------------
# Run server
# --------------------------

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

    app.run(debug=True)
