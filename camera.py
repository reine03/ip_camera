from flask import Blueprint, Response, request
from database.models import db, CameraLog
import cv2

camera_bp = Blueprint('camera', __name__)

def generate_frames():
    cap = cv2.VideoCapture(0)  # 0 = built-in webcam
    while True:
        success, frame = cap.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    cap.release()

@camera_bp.route('/video_feed')
def video_feed():
    ip_address = request.remote_addr
    # Log camera started
    log = CameraLog(event='started', ip_address=ip_address)
    db.session.add(log)
    db.session.commit()
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')