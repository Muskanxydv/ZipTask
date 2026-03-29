from models import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    payment = db.Column(db.Integer)
    status = db.Column(db.String(20), default="open")
    posted_by = db.Column(db.String(50), nullable=True)
    assigned_to = db.Column(db.String(50), nullable=True)
    payment_status = db.Column(db.String(20), default="unpaid") 

class TaskUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(255), nullable=False)
    percentage = db.Column(db.Integer, nullable=False)
    proof_image = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
class TaskApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, nullable=False)
    worker_id = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="pending")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
