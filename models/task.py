import uuid
from models import db

class Task(db.Model):

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    title = db.Column(db.String(200), nullable=False)

    description = db.Column(db.Text, nullable=False)

    category = db.Column(db.String(50))

    payment = db.Column(db.Integer)

    status = db.Column(db.String(20), default="open")

    posted_by = db.Column(db.String(36), db.ForeignKey("user.id"))

    accepted_by = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=True)
