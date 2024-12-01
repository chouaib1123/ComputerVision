import cv2
import face_recognition
import logging
import os
from Model import Person

logger = logging.getLogger(__name__)

class FaceRecognitionSystem:
    def __init__(self, persons=None):
        self.scale_factor = 0.25
        self.known_face_encodings = {}  # Dict of name: encoding
        if persons:
            self.load_initial_faces(persons)

    def load_initial_faces(self, persons):
        """Load all faces on startup"""
        for person in persons:
            self.add_person(person)

    def add_person(self, person):
        """Add or update a single person's face encoding"""
        try:
            if os.path.exists(person.image_path):
                image = face_recognition.load_image_file(person.image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    self.known_face_encodings[person.name] = encodings[0]
                    logger.info(f"Added face encoding for {person.name}")
                    return True
                else:
                    logger.warning(f"No face found in image for {person.name}")
            else:
                logger.error(f"Image file missing: {person.image_path}")
        except Exception as e:
            logger.error(f"Error processing {person.name}'s image: {str(e)}")
        return False

    def process_frame(self, frame, persons=None):
        """Process frame using cached encodings. Optional persons param to update cache."""
        try:
            if persons:
                self.load_initial_faces(persons)
                
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            small_frame = cv2.resize(rgb_frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
            face_locations = face_recognition.face_locations(small_frame)
            results = []

            if face_locations:
                face_encodings = face_recognition.face_encodings(small_frame, face_locations)
                for face_encoding, face_location in zip(face_encodings, face_locations):
                    name = "Unknown"
                    for person_name, known_encoding in self.known_face_encodings.items():
                        match = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.6)[0]
                        if match:
                            name = person_name
                            break
                    results.append({"name": name, "location": face_location})
                    logger.info(f"Face recognized: {name}")
            return results
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            return []

def identify_person_from_results(results):
    for result in results:
        if result["name"] != "Unknown":
            return result["name"]
    return "Unknown"