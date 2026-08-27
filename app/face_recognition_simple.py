import cv2
import numpy as np
import os
from PIL import Image
import pickle

class SimpleFaceRecognition:
    """
    Simple face recognition using basic image comparison
    This doesn't require dlib or complex OpenCV face detection
    """
    
    def __init__(self):
        self.trained = False
        print("Using basic image comparison for face recognition")
        
    def detect_faces(self, image):
        """Simple face detection - returns entire image as face region"""
        # For simplicity, we'll use the entire image
        # In a production system, you'd want proper face detection
        return [(0, 0, image.shape[1], image.shape[0])], cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def extract_face_encoding(self, image_path):
        """
        Extract a simple image encoding for comparison
        Returns a simple encoding based on image features
        """
        if not os.path.exists(image_path):
            return None
        
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        try:
            # Convert to grayscale and resize to standard size
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (100, 100))
            
            # Use the resized image as encoding
            encoding = resized.flatten()
            
            return encoding
        except Exception as e:
            print(f"Error extracting encoding: {e}")
            return None
    
    def compare_faces(self, encoding1, encoding2, threshold=0.7):
        """
        Compare two image encodings using improved correlation
        Returns True if images match, False otherwise
        """
        if encoding1 is None or encoding2 is None:
            return False, 0.0
        
        try:
            # Reshape encodings if needed
            if encoding1.ndim == 1:
                encoding1 = encoding1.reshape(100, 100)
            if encoding2.ndim == 1:
                encoding2 = encoding2.reshape(100, 100)
            
            # Normalize both encodings
            encoding1_norm = cv2.normalize(encoding1.astype(np.float32), None, 0, 1, cv2.NORM_MINMAX)
            encoding2_norm = cv2.normalize(encoding2.astype(np.float32), None, 0, 1, cv2.NORM_MINMAX)
            
            # Use multiple template matching methods
            methods = [cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF]
            similarities = []
            
            for method in methods:
                try:
                    result = cv2.matchTemplate((encoding1_norm * 255).astype(np.uint8), 
                                               (encoding2_norm * 255).astype(np.uint8), 
                                               method)
                    _, max_val, _, _ = cv2.minMaxLoc(result)
                    
                    # For SQDIFF, lower is better, so invert
                    if method == cv2.TM_SQDIFF:
                        max_val = 1.0 - max_val
                    
                    similarities.append(max_val)
                except:
                    continue
            
            # Use the best similarity score
            if similarities:
                best_similarity = max(similarities)
            else:
                # Fallback to simple correlation
                result = cv2.matchTemplate(encoding1.astype(np.uint8), 
                                           encoding2.astype(np.uint8), 
                                           cv2.TM_CCOEFF_NORMED)
                _, best_similarity, _, _ = cv2.minMaxLoc(result)
            
            return best_similarity > threshold, best_similarity
        except Exception as e:
            # Ultimate fallback: simple pixel comparison
            try:
                diff = np.abs(encoding1 - encoding2)
                similarity = 1.0 - (np.mean(diff) / 255.0)
                return similarity > threshold, similarity
            except:
                return False, 0.0