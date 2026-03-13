from flask import Blueprint, request, jsonify
from models.task import Task

dashboard_bp = Blueprint("dashboard", __name__)


# Get tasks by category filter
@dashboard_bp.route("/tasks", methods=["GET"])
def get_tasks():

    category = request.args.get("category")

    if category:
        tasks = Task.query.filter_by(category=category, status="open").all()
    else:
        tasks = Task.query.filter_by(status="open").all()

    result = []

    for task in tasks:
        result.append({
            "id": task.id,
            "title": task.title,
            "category": task.category,
            "payment": task.payment
        })

    return jsonify(result)
