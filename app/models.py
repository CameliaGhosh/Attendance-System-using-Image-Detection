from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    face_encoding = db.Column(db.Text, nullable=True)
    face_image_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    attendance_records = db.relationship('Attendance', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name}>'

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    check_out_time = db.Column(db.DateTime, nullable=True)
    date = db.Column(db.Date, default=datetime.utcnow().date())
    status = db.Column(db.String(20), default='present')
    confidence = db.Column(db.Float, nullable=True)
    
    def __repr__(self):
        return f'<Attendance {self.user_id} - {self.check_in_time}>'