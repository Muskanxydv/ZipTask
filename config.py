import os

class Config:
    SECRET_KEY = "ziptask_secret_key"

    SQLALCHEMY_DATABASE_URI = "sqlite:///ziptask.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
