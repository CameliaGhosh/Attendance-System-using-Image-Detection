from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from app.models import User, Attendance
from app.face_recognition_simple import SimpleFaceRecognition
import os
from datetime import datetime, timezone, timedelta
import cv2
import numpy as np
import base64

# Set timezone to IST (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Routes using simple OpenCV-based face recognition
# This provides face recognition functionality without requiring dlib

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/attendance')
def attendance():
    return render_template('attendance.html')

@app.route('/reports')
def reports():
    users = User.query.all()
    attendance_records = Attendance.query.order_by(Attendance.check_in_time.desc()).all()
    return render_template('reports.html', users=users, attendance_records=attendance_records)

@app.route('/api/register_user', methods=['POST'])
def register_user():
    try:
        name = request.form.get('name')
        employee_id = request.form.get('employee_id')
        email = request.form.get('email')
        
        if 'face_image' not in request.files:
            return jsonify({'success': False, 'message': 'No face image provided'})
        
        file = request.files['face_image']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        if file:
            filename = f"{employee_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Use simple face recognition to extract encoding
            face_rec = SimpleFaceRecognition()
            encoding = face_rec.extract_face_encoding(filepath)
            
            if encoding is None:
                os.remove(filepath)
                return jsonify({'success': False, 'message': 'No face detected in the image'})
            
            # Convert encoding to string for storage
            encoding_str = ','.join(map(str, encoding))
            
            # Check if employee_id already exists
            existing_user = User.query.filter_by(employee_id=employee_id).first()
            if existing_user:
                os.remove(filepath)
                return jsonify({'success': False, 'message': 'Employee ID already exists'})
            
            # Create new user with face encoding
            new_user = User(
                name=name,
                employee_id=employee_id,
                email=email,
                face_encoding=encoding_str,
                face_image_path=filename
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'User registered successfully with face encoding'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/mark_attendance', methods=['POST'])
def mark_attendance():
    try:
        data = request.json
        
        # Handle both camera mode (with image) and manual mode (with employee_id)
        if 'image' in data:
            # Camera mode - use simple face recognition
            image_data = data.get('image')
            
            if not image_data:
                return jsonify({'success': False, 'message': 'No image data provided'})
            
            # Decode base64 image
            image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            
            # Convert to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return jsonify({'success': False, 'message': 'Failed to decode image'})
            
            # Save temporary image for processing
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_capture.jpg')
            cv2.imwrite(temp_path, img)
            
            # Extract face encoding from captured image
            face_rec = SimpleFaceRecognition()
            captured_encoding = face_rec.extract_face_encoding(temp_path)
            
            if captured_encoding is None:
                os.remove(temp_path)
                return jsonify({'success': False, 'message': 'No face detected in captured image'})
            
            # Get all registered users with face encodings
            users = User.query.filter(User.face_encoding.isnot(None)).all()
            
            if not users:
                os.remove(temp_path)
                return jsonify({'success': False, 'message': 'No registered users with face data found'})
            
            best_match = None
            best_similarity = 0.0
            
            for user in users:
                if user.face_encoding:
                    try:
                        stored_encoding = np.array(list(map(float, user.face_encoding.split(','))))
                        matches, similarity = face_rec.compare_faces(captured_encoding, stored_encoding, threshold=0.4)  # Adjusted threshold
                        
                        if matches and similarity > best_similarity:
                            best_similarity = similarity
                            best_match = user
                    except Exception as e:
                        continue
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if best_match and best_similarity > 0.4:  # Adjusted threshold
                # Check if already marked attendance today
                today = datetime.now().date()
                existing_attendance = Attendance.query.filter_by(
                    user_id=best_match.id,
                    date=today
                ).first()
                
                if existing_attendance:
                    return jsonify({
                        'success': True,
                        'message': f'Attendance already marked for {best_match.name} today',
                        'user': best_match.name,
                        'time': existing_attendance.check_in_time.strftime('%I:%M %p'),  # 12-hour format with AM/PM
                        'already_marked': True
                    })
                
                # Mark attendance with IST time
                utc_time = datetime.now(timezone.utc)
                ist_time = utc_time.astimezone(IST)
                new_attendance = Attendance(
                    user_id=best_match.id,
                    confidence=best_similarity
                )
                new_attendance.check_in_time = ist_time.replace(tzinfo=None)
                
                db.session.add(new_attendance)
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': f'Attendance marked for {best_match.name}',
                    'user': best_match.name,
                    'time': new_attendance.check_in_time.strftime('%I:%M %p'),  # 12-hour format with AM/PM
                    'confidence': round(best_similarity * 100, 2),
                    'already_marked': False
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Face not recognized or confidence too low'
                })
        
        # Manual mode
        employee_id = data.get('employee_id')
        
        if not employee_id:
            return jsonify({'success': False, 'message': 'Employee ID required'})
        
        # Find user by employee ID
        user = User.query.filter_by(employee_id=employee_id).first()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})
        
        # Check if already marked attendance today
        today = datetime.now().date()
        existing_attendance = Attendance.query.filter_by(
            user_id=user.id,
            date=today
        ).first()
        
        if existing_attendance:
            return jsonify({
                'success': True,
                'message': f'Attendance already marked for {user.name} today',
                'user': user.name,
                'time': existing_attendance.check_in_time.strftime('%I:%M %p'),  # 12-hour format with AM/PM
                'already_marked': True
            })
        
        # Mark attendance with IST time
        utc_time = datetime.now(timezone.utc)
        ist_time = utc_time.astimezone(IST)
        new_attendance = Attendance(
            user_id=user.id,
            confidence=1.0  # Manual entry has 100% confidence
        )
        new_attendance.check_in_time = ist_time.replace(tzinfo=None)
        
        db.session.add(new_attendance)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Attendance marked for {user.name}',
            'user': user.name,
            'time': new_attendance.check_in_time.strftime('%I:%M %p'),  # 12-hour format with AM/PM
            'confidence': 1.0,
            'already_marked': False
        })
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/get_users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'name': user.name,
            'employee_id': user.employee_id,
            'email': user.email,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(user_list)

@app.route('/api/get_attendance', methods=['GET'])
def get_attendance():
    date_str = request.args.get('date')
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        attendance_records = Attendance.query.filter_by(date=date).all()
    else:
        attendance_records = Attendance.query.order_by(Attendance.check_in_time.desc()).all()
    
    records = []
    for record in attendance_records:
        records.append({
            'id': record.id,
            'user_name': record.user.name,
            'employee_id': record.user.employee_id,
            'check_in_time': record.check_in_time.strftime('%I:%M %p'),
            'date': record.date.strftime('%Y-%m-%d'),
            'status': record.status
        })
    
    return jsonify(records)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)