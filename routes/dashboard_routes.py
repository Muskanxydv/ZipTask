from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from models.task import Task,TaskUpdate, TaskApplication
from models.user import User
from models import db
import os
from werkzeug.utils import secure_filename
from flask import current_app 

dashboard_bp = Blueprint("dashboard", __name__)


# -----------------------------
# Dashboard Page
# -----------------------------
@dashboard_bp.route("/dashboard")
def dashboard_page():

    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))

    user = User.query.get(session["user_id"])

    return render_template("dashboard.html", user=user)


# -----------------------------
# Get Available Tasks Near You
# -----------------------------
@dashboard_bp.route("/tasks", methods=["GET"])
def get_tasks():
    user_id = session.get("user_id")
    category = request.args.get("category")

    query = Task.query.filter(
        Task.status == "open", 
        Task.posted_by != user_id,
        Task.posted_by != str(user_id)
    )

    if category and category != "all":
        query = query.filter(Task.category == category)

    tasks = query.all()

    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "category": t.category,
            "payment": t.payment,
            "description": t.description
        } for t in tasks
    ])
# -----------------------------
# Get My Personal Tasks
# -----------------------------
@dashboard_bp.route("/my-tasks", methods=["GET"])
def get_my_tasks():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user_id = session["user_id"]

    posted_tasks = Task.query.filter_by(posted_by=user_id).all()
    accepted_tasks = Task.query.filter_by(assigned_to=user_id).all()

    def serialize_task(t, role):
        updates = TaskUpdate.query.filter_by(task_id=t.id).order_by(TaskUpdate.timestamp.asc()).all()

        contact_name = "Waiting for worker..."
        contact_phone = None
        
        if role == "poster" and t.assigned_to:
            worker = User.query.get(int(t.assigned_to))
            if worker:
                contact_name = worker.name
                contact_phone = worker.phone
        elif role == "worker" and t.posted_by:
            poster = User.query.get(int(t.posted_by))
            if poster:
                contact_name = poster.name
                contact_phone = poster.phone

        return {
            "id": t.id, "title": t.title, "status": t.status, 
            "payment": t.payment, "payment_status": t.payment_status, 
            "category": t.category, "description": t.description,
            "contact_name": contact_name, 
            "contact_phone": contact_phone,
            "updates": [{"message": u.message, "percentage": u.percentage, 
                         "time": u.timestamp.strftime("%b %d, %I:%M %p"), 
                         "proof_image": u.proof_image} for u in updates]
        }

    return jsonify({
        "posted": [serialize_task(t, "poster") for t in posted_tasks],
        "accepted": [serialize_task(t, "worker") for t in accepted_tasks]
    })


# -----------------------------
# Post Task Update (With Image Upload)
# -----------------------------
@dashboard_bp.route("/add-task-update/<int:task_id>", methods=["POST"])
def add_task_update(task_id):
    if "user_id" not in session: return jsonify({"error": "Unauthorized"}), 401
        
    task = Task.query.get(task_id)

    message = request.form.get("message")
    percentage = int(request.form.get("percentage"))

    if percentage > 50 and task.payment_status == "unpaid":
        return jsonify({"error": "Cannot update past 50% until requester releases the first milestone payment."}), 400

    proof_filename = None
    if 'proof' in request.files:
        file = request.files['proof']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            proof_filename = f"task_{task.id}_proof_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], proof_filename)
            file.save(filepath)

    new_update = TaskUpdate(
        task_id=task_id, message=message, percentage=percentage, proof_image=proof_filename
    )
    db.session.add(new_update)
    db.session.commit()
    return jsonify({"message": "Status & proof uploaded successfully!"})


# -----------------------------
# Process Milestone Payments
# -----------------------------
@dashboard_bp.route("/process-payment/<int:task_id>", methods=["POST"])
def process_payment(task_id):
    if "user_id" not in session: return jsonify({"error": "Unauthorized"}), 401
    
    task = Task.query.get(task_id)
    if task.posted_by != str(session["user_id"]):
        return jsonify({"error": "Only the poster can make payments."}), 403
        
    if task.payment_status == "unpaid":
        task.payment_status = "half_paid"
        msg = "50% Milestone released successfully!"
    elif task.payment_status == "half_paid":
        task.payment_status = "fully_paid"
        task.status = "completed"
        msg = "Final payment released and task completed!"
        
    db.session.commit()
    return jsonify({"message": msg})


# -----------------------------
# Post Task
# -----------------------------
@dashboard_bp.route("/post-task", methods=["POST"])
def post_task():

    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))

    new_task = Task(
        title=request.form["title"],
        description=request.form["description"],
        category=request.form["category"],
        payment=request.form["payment"],
        status="open",
        posted_by=session["user_id"]
    )

    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for("dashboard.dashboard_page"))


# -----------------------------
# 1. Apply for a Task
# -----------------------------
@dashboard_bp.route("/apply-task/<int:task_id>", methods=["POST"])
def apply_task(task_id):
    if "user_id" not in session: return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session["user_id"]
    data = request.get_json()
    message = data.get("message", "I can help with this!")

    existing = TaskApplication.query.filter_by(task_id=task_id, worker_id=str(user_id)).first()
    if existing:
        return jsonify({"error": "You have already applied for this task."}), 400

    new_app = TaskApplication(task_id=task_id, worker_id=str(user_id), message=message)
    db.session.add(new_app)
    db.session.commit()
    
    return jsonify({"message": "Application submitted! The poster will review your pitch."})

# -----------------------------
# 2. Review Page View
# -----------------------------
@dashboard_bp.route("/review-applicants/<int:task_id>")
def review_page(task_id):
    if "user_id" not in session: return redirect(url_for("auth.login_page"))
    
    user = User.query.get(session["user_id"])
    task = Task.query.get(task_id)
    
    if not task or task.posted_by != str(user.id):
        return redirect(url_for("dashboard.dashboard_page"))
        
    return render_template("review_applicants.html", user=user, task=task)

# -----------------------------
# 3. Get Applicants API
# -----------------------------
@dashboard_bp.route("/api/applicants/<int:task_id>")
def get_applicants(task_id):
    apps = TaskApplication.query.filter_by(task_id=task_id, status="pending").all()
    
    result = []
    for app in apps:
        worker = User.query.get(int(app.worker_id))
        if worker:
            avg_rating = round(worker.total_rating / worker.rating_count, 1) if worker.rating_count > 0 else 5.0
            result.append({
                "id": app.id,
                "worker_name": worker.name,
                "worker_pic": worker.profile_pic,
                "message": app.message,
                "rating": avg_rating,
                "tasks_completed": worker.tasks_completed
            })
    return jsonify(result)

# -----------------------------
# 4. Hire Worker!
# -----------------------------
@dashboard_bp.route("/hire-worker/<int:application_id>", methods=["POST"])
def hire_worker(application_id):
    if "user_id" not in session: return jsonify({"error": "Unauthorized"}), 401
    
    app = TaskApplication.query.get(application_id)
    task = Task.query.get(app.task_id)

    task.status = "assigned"
    task.assigned_to = app.worker_id
    
    app.status = "accepted"
    TaskApplication.query.filter(TaskApplication.task_id == task.id, TaskApplication.id != app.id).update({"status": "rejected"})
    
    db.session.commit()
    return jsonify({"message": f"Successfully hired {app.worker_id}! Task moved to active."})

# -----------------------------
# Unassign Worker & Relist Task
# -----------------------------
@dashboard_bp.route("/unassign-task/<int:task_id>", methods=["POST"])
def unassign_task(task_id):
    if "user_id" not in session: 
        return jsonify({"error": "Unauthorized"}), 401
    
    task = Task.query.get(task_id)
    
    if task.posted_by != str(session["user_id"]):
        return jsonify({"error": "Only the task poster can unassign a worker."}), 403
        
    if task.payment_status != "unpaid":
        return jsonify({"error": "You cannot unassign a worker after milestone payments have been made."}), 400

    task.status = "open"
    task.assigned_to = None
    
    TaskUpdate.query.filter_by(task_id=task.id).delete()
    
    db.session.commit()
    return jsonify({"message": "Worker removed. Task is back on the open feed!"})

# -----------------------------
# Get Leaderboard Data
# -----------------------------
@dashboard_bp.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    top_workers = User.query.filter(User.tasks_completed > 0).order_by(User.tasks_completed.desc()).limit(10).all()
    
    leaderboard_data = []
    for worker in top_workers:
        avg_rating = round(worker.total_rating / worker.rating_count, 1) if worker.rating_count > 0 else 5.0
        
        leaderboard_data.append({
            "name": worker.name,
            "tasks_completed": worker.tasks_completed,
            "rating": avg_rating,
            "profile_pic": worker.profile_pic
        })
        
    return jsonify(leaderboard_data)

# -----------------------------
# Leaderboard Page
# -----------------------------
@dashboard_bp.route("/leaderboard")
def leaderboard_page():
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))
    
    user = User.query.get(session["user_id"])
    return render_template("leaderboard.html", user=user)
# -----------------------------
# Logout
# -----------------------------
@dashboard_bp.route("/logout")
def logout():

    session.pop("user_id", None)
    return redirect(url_for("auth.login_page"))

# -----------------------------
# Profile Page (View)
# -----------------------------
@dashboard_bp.route("/profile")
def profile_page():
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))
    
    user = User.query.get(session["user_id"])
    return render_template("profile.html", user=user)

# -----------------------------
# Update Profile (Process Form)
# -----------------------------
@dashboard_bp.route("/update-profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))

    user = User.query.get(session["user_id"])

    user.name = request.form.get("name")
    user.phone = request.form.get("phone")
    user.gender = request.form.get("gender")
    user.dob = request.form.get("dob")
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        
        if file and file.filename != '':

            filename = secure_filename(file.filename)

            unique_filename = f"user_{user.id}_{filename}"
            
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            user.profile_pic = unique_filename

    db.session.commit()
    return redirect(url_for("dashboard.profile_page"))
