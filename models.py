from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='viewer')

class LoginLog(db.Model):
    __tablename__ = 'login_logs'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'success' or 'failed'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class CameraLog(db.Model):
    __tablename__ = 'camera_logs'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(50), nullable=False)  # 'started' or 'stopped'
    ip_address = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)