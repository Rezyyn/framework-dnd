# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dnd.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
