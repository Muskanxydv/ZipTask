from flask import Flask, render_template
from models import db
from models.user import User
from models.task import Task

# import routes
from routes.auth_routes import auth_bp

app = Flask(__name__)

# configuration
app.config["SECRET_KEY"] = "ziptask_secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ziptask.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# initialize database
db.init_app(app)

# register routes
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

@app.route("/login")
def login():
    return render_template("login_page.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot_password.html")


# --------------------------
# Dashboard
# --------------------------

@app.route("/dashboard/<int:user_id>")
def dashboard(user_id):

    # get user from database
    user = User.query.get_or_404(user_id)

    # tasks that are not accepted yet
    tasks = Task.query.filter_by(status="open").all()

    # check if user already accepted a task
    current_task = Task.query.filter_by(
        accepted_by=user_id,
        status="accepted"
    ).first()

    return render_template(
        "dashboard.html",
        user=user,
        tasks=tasks,
        current_task=current_task
    )


# --------------------------
# Run server
# --------------------------

if __name__ == "__main__":

    with app.app_context():

        # create database tables if they don't exist
        db.create_all()

    app.run(debug=True)
