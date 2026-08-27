# Facial Recognition Attendance System
 
An automated attendance management system that uses AI-powered face recognition technology to eliminate manual intervention in attendance tracking.
 
## Features
 
- **Real-time Face Recognition**: Uses OpenCV template matching algorithms to identify registered users automatically
- **Dual-Mode Operation**: Supports both camera-based face recognition and manual Employee ID fallback
- **Web-Based Interface**: Clean, responsive web interface built with Flask and Bootstrap 5
- **IST Timezone Support**: Accurate local time recording (UTC+5:30) for precise attendance tracking
- **Database Management**: SQLite database with SQLAlchemy ORM for efficient data storage
- **Comprehensive Reporting**: View attendance history, user statistics, and filter records by date
 
## Technical Stack
 
- **Backend**: Python 3.14, Flask 3.1.3, Flask-SQLAlchemy 3.1.1
- **Face Recognition**: OpenCV 5.0.0, NumPy 2.5.0
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5.1.3
- **Image Processing**: Pillow 12.3.0, imutils 0.5.4
 
## Installation
 
1. Navigate to the project directory:
```bash
cd attendance_system
```
 
2. Install required packages:
```bash
pip install Flask Flask-SQLAlchemy opencv-python numpy Pillow imutils
```
 
3. Run the application:
```bash
python run.py
```
 
4. Open browser to `http://localhost:5000`
 
## Usage
 
### User Registration
1. Navigate to the "Register" page
2. Fill in user details (name, employee ID, email)
3. Upload a face photo or capture one using the camera
4. Click "Register User"
 
### Marking Attendance
 
**Camera Mode:**
1. Navigate to the "Mark Attendance" page
2. Click "Start Camera" to activate webcam
3. Position your face in front of the camera
4. Click "Mark Attendance"
 
**Manual Mode:**
1. Switch to "Manual Mode"
2. Enter your Employee ID
3. Click "Mark Attendance"
 
### Viewing Reports
1. Navigate to the "Reports" page
2. View all registered users and attendance records
3. Filter records by date
 
## Project Structure
 
```
attendance_system/
├── app/
│   ├── __init__.py                    # Flask app initialization
│   ├── face_recognition_simple.py     # Face recognition logic
│   ├── models.py                      # Database models
│   ├── routes_basic.py                 # API routes
│   ├── static/
│   │   ├── css/style.css              # Custom styling
│   │   └── js/main.js                 # JavaScript utilities
│   └── templates/
│       ├── attendance.html             # Attendance marking page
│       ├── base.html                   # Base template
│       ├── index.html                  # Home page
│       ├── register.html               # Registration page
│       └── reports.html                # Reports page
├── instance/
│   └── attendance.db                  # SQLite database
├── uploads/                           # User uploaded images
└── run.py                             # Application entry point
```
 
## How It Works
 
1. **Registration**: Users register with their face photos, which are processed to generate unique facial encodings
2. **Face Recognition**: When marking attendance, the system captures a live camera frame and compares it with stored facial encodings using multiple template matching methods
3. **Attendance Logging**: If a match is found with sufficient confidence, attendance is recorded with IST timestamp
4. **Reporting**: All attendance records are stored in the database and can be viewed through the web interface
 
