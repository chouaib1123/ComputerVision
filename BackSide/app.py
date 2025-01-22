import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import numpy as np
import cv2
import logging
from face_recognition_system import FaceRecognitionSystem, identify_person_from_results
from presence_manager import PresenceManager
from Model import add_person , Person
from flask_socketio import SocketIO, emit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = '.\\Images'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

presence_manager = PresenceManager(db_url="sqlite:///presence.db")

# Initialize face system with all persons
session = presence_manager.get_session()
try:
    initial_persons = session.query(Person).all()
    face_system = FaceRecognitionSystem(initial_persons)
finally:
    session.close()

socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/process-frame', methods=['POST'])
def process_frame():
    try:
        if not request.json or 'frame' not in request.json:
            return jsonify({"success": False, "error": "Missing frame data"}), 400

        frame_data = request.json['frame']
        if frame_data.startswith('data:image'):
            frame_data = frame_data.split(',')[1]

        img_bytes = base64.b64decode(frame_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"success": False, "error": "Invalid frame data"}), 400

        # Pass frame only since we maintain cache
        results = face_system.process_frame(frame)
        person_name = identify_person_from_results(results)

        if person_name == "Unknown":
            return jsonify({"success": True, "message": "Unknown person"}), 200

        success, message = presence_manager.store_presence(person_name)
        if success:
            persons_data = presence_manager.get_all_persons_with_presence()
            socketio.emit('persons_data', persons_data)
            
        return jsonify({"success": success, "message": message}), 200

    except Exception as e:
        logger.error(f"Error processing frame: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/upload-image', methods=['POST'])
def upload_image():
    image_path = None
    try:
        if 'name' not in request.form or 'image' not in request.files:
            return jsonify({"success": False, "error": "Missing data"}), 400

        name = request.form['name']
        image_file = request.files['image']
        image_path = os.path.join(UPLOAD_FOLDER, image_file.filename)
        image_file.save(image_path)

        session = presence_manager.Session()
        try:
            person = add_person(session, name, image_path)
            face_system.add_person(person)
            
            # Emit updated persons data after successful addition
            persons_data = presence_manager.get_all_persons_with_presence()
            socketio.emit('persons_data', persons_data)
            
            return jsonify({"success": True, "message": "Person added successfully"}), 200
        except Exception as e:
            session.rollback()
            if os.path.exists(image_path):
                os.remove(image_path)
            return jsonify({"success": False, "error": f"Database error: {str(e)}"}), 500
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/get-all-persons', methods=['GET'])
def get_all_persons():
    try:
        persons_with_presence = presence_manager.get_all_persons_with_presence()
        return jsonify(persons_with_presence), 200
    except Exception as e:
        logger.error(f"Error fetching all persons with presence: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@socketio.on('connect')
def handle_connect():
    try:
        persons_data = presence_manager.get_all_persons_with_presence()
        emit('persons_data', persons_data)
    except Exception as e:
        logger.error(f"Error sending initial data: {str(e)}")



if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)