import os

class Config:
    # Secret key used for sessions/security
    SECRET_KEY = "ziptask_secret_key"

    # SQLite database location
    SQLALCHEMY_DATABASE_URI = "sqlite:///ziptask.db"

    # Disables unnecessary warnings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
