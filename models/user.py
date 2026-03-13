from models import db


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    phone = db.Column(db.String(15), nullable=False)

    password = db.Column(db.String(200), nullable=False)

    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
