from models import db

class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    description = db.Column(db.Text, nullable=False)

    category = db.Column(db.String(50))

    payment = db.Column(db.Integer)

    status = db.Column(db.String(20), default="open")

    posted_by = db.Column(db.Integer, db.ForeignKey("user.id"))

    accepted_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
