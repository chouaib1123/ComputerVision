import cv2
import face_recognition
import logging
import os
import numpy as np
import pickle
from enum import Enum
from Model import Person  # Assuming you have a 'Person' class in a 'Model.py'

# Logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class FaceDetectionStatus(Enum):
    NOT_DETECTED = "Please fix your face position"
    DETECTED = "Face detected"

class FaceRecognitionSystem:
    def __init__(self, persons=None):
        self.scale_factor = 0.25
        self.known_face_encodings = {}
        self.cache_file = "face_encodings_cache.pkl"
        self.confidence_threshold = 0.6
        self.MIN_FACE_HEIGHT = 70
        self.MAX_FACE_HEIGHT = 200
        if persons:
            self.load_or_create_encodings(persons)

    def load_or_create_encodings(self, persons):
        """Load encodings from cache or create new ones"""
        if os.path.exists(self.cache_file):
            self.load_cached_encodings()
        else:
            self.create_new_encodings(persons)

    def load_cached_encodings(self):
        """Load encodings from cache file"""
        try:
            with open(self.cache_file, 'rb') as f:
                self.known_face_encodings = pickle.load(f)
            logger.info("Loaded cached face encodings")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            self.known_face_encodings = {}

    def save_cached_encodings(self):
        """Save encodings to cache file"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.known_face_encodings, f)
            logger.info("Saved face encodings to cache")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def create_new_encodings(self, persons):
        """Create new encodings for all persons"""
        for person in persons:
            try:
                self.add_person(person)
            except Exception as e:
                logger.error(f"Failed to create encoding for {person.name}: {str(e)}")
                continue

    def preprocess_image(self, image):
        """Enhanced image preprocessing pipeline"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        normalized = cv2.normalize(enhanced, None, 0, 255, cv2.NORM_MINMAX)
        return cv2.cvtColor(normalized)

    def add_person(self, person):
        """Add new person to face recognition system"""
        try:
            # Load and validate image
            image = face_recognition.load_image_file(person.image_path)
            if image is None:
                raise ValueError(f"Failed to load image from {person.image_path}")

            # Get face encoding
            face_locations = face_recognition.face_locations(image)
            if not face_locations:
                raise ValueError("No face detected in image")
            
            face_encoding = face_recognition.face_encodings(image, face_locations)[0]
            
            # Store encoding
            self.known_face_encodings[person.name] = face_encoding
            
            # Update cache
            self.save_cached_encodings()
            
            logger.info(f"Successfully added person {person.name}")
            return True

        except Exception as e:
            logger.error(f"Error adding person {person.name}: {str(e)}")
            raise

    def get_face_angle(self, landmarks):
        """Calculate face rotation angle from landmarks"""
        left_eye = np.mean(landmarks['left_eye'], axis=0)
        right_eye = np.mean(landmarks['right_eye'], axis=0)
        return np.degrees(np.arctan2(right_eye[1] - left_eye[1], right_eye[0] - left_eye[0]))

    def align_face(self, image, landmarks):
        """Align face to be upright based on eye positions"""
        left_eye = np.mean(landmarks['left_eye'], axis=0)
        right_eye = np.mean(landmarks['right_eye'], axis=0)
        angle = self.get_face_angle(landmarks)
        center = ((left_eye[0] + right_eye[0]) // 2, (left_eye[1] + right_eye[1]) // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))

    def check_face_features(self, landmarks):
        """Verify all required facial features are clearly visible"""
        for feature, min_points in self.required_landmarks.items():
            if len(landmarks.get(feature, [])) < min_points:
                return FaceDetectionStatus.UNCLEAR, 0.0
        return FaceDetectionStatus.DETECTED, 1.0

    def check_face_distance(self, face_location):
        """Check if face is at optimal distance"""
        face_height = face_location[2] - face_location[0]
        MIN_FACE_HEIGHT, MAX_FACE_HEIGHT = 70, 200
        if face_height < MIN_FACE_HEIGHT:
            return FaceDetectionStatus.TOO_FAR, 0.0
        if face_height > MAX_FACE_HEIGHT:
            return FaceDetectionStatus.TOO_CLOSE, 0.0
        return FaceDetectionStatus.DETECTED, 1.0

    def check_face_quality(self, face_image, face_location):
        """Check if face is clearly visible"""
        try:
            landmarks_list = face_recognition.face_landmarks(face_image, [face_location])
            if not landmarks_list or len(landmarks_list[0]) < 5:
                return FaceDetectionStatus.NOT_DETECTED, 0.0
            return FaceDetectionStatus.DETECTED, 1.0
        except Exception as e:
            logger.error(f"Quality check error: {e}")
            return FaceDetectionStatus.NOT_DETECTED, 0.0

    def recognize_face(self, face_encoding, face_image, face_location):
        """Face recognition with basic quality check"""
        status, quality_score = self.check_face_quality(face_image, face_location)
        if status != FaceDetectionStatus.DETECTED:
            return status.value, 0.0

        # Continue with existing recognition logic
        best_match, best_score = "Unknown", float('inf')
        for person_name, known_encodings in self.known_face_encodings.items():
            distances = [np.linalg.norm(face_encoding - known_enc) for known_enc in known_encodings]
            avg_distance = np.mean(distances)
            if avg_distance < best_score:
                best_score, best_match = avg_distance, person_name

        confidence = 1 / (1 + best_score)
        if confidence > self.confidence_threshold:
            return best_match, confidence
        return "Unknown", confidence

    def process_frame(self, frame):
        try:
            # Convert frame to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_frame)
            if not face_locations:
                return []

            # Get encodings
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            
            results = []
            for face_encoding, face_location in zip(face_encodings, face_locations):
                # Calculate distances
                face_distances = face_recognition.face_distance(
                    list(self.known_face_encodings.values()), 
                    face_encoding
                )
                
                logger.debug(f"Known encodings count: {len(self.known_face_encodings)}")
                logger.debug(f"Face distances: {face_distances}")
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    min_distance = face_distances[best_match_index]
                    
                    if min_distance <= self.confidence_threshold:
                        name = list(self.known_face_encodings.keys())[best_match_index]
                        logger.info(f"Match found: {name} with distance {min_distance}")
                        results.append({
                            "name": name,
                            "confidence": 1 - min_distance,
                            "location": face_location
                        })
                    else:
                        logger.debug(f"No match found. Best distance: {min_distance}")
                
            return results
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            return []

    def verify_image(self, image):
        """
        Verify if image contains a detectable face
        Returns: bool
        """
        try:
            # Convert to RGB if needed
            if len(image.shape) == 2:  # Grayscale
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 3:  # BGR
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(image)
            
            # Check if at least one face was detected
            return len(face_locations) > 0
            
        except Exception as e:
            logger.error(f"Error verifying image: {e}")
            return False


def identify_person_from_results(results):
    """Identify the person from recognition results"""
    for result in results:
        if result["name"] != "Unknown":
            return result["name"]
    return "Unknown"
