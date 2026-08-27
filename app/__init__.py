from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')

db = SQLAlchemy(app)

# Try to import face recognition routes, fall back to basic routes
try:
    from app import routes
    print("Using advanced face recognition routes (dlib-based)")
except ImportError:
    try:
        from app import routes_basic as routes
        print("Using OpenCV-based face recognition routes")
    except ImportError:
        print("No routes available - system not functional")