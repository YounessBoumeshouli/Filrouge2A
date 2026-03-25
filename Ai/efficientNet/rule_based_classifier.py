#!/usr/bin/env python3
"""
Rule-based classifier for immediate accuracy improvement
"""

import base64
import numpy as np
from PIL import Image
from io import BytesIO
import cv2

class RuleBasedClassifier:
    def __init__(self):
        self.categories = {
            "spices": {"colors": [(255, 165, 0), (255, 140, 0), (255, 69, 0)], "keywords": ["powder", "grain"]},
            "textiles": {"colors": [(128, 0, 128), (255, 20, 147), (0, 100, 0)], "keywords": ["fabric", "pattern"]},
            "leather": {"colors": [(139, 69, 19), (160, 82, 45), (210, 180, 140)], "keywords": ["brown", "tan"]},
            "jewelry": {"colors": [(255, 215, 0), (192, 192, 192), (255, 255, 0)], "keywords": ["gold", "silver"]},
            "crafts": {"colors": [(165, 42, 42), (128, 128, 0), (255, 99, 71)], "keywords": ["wood", "ceramic"]},
            "lanterns": {"colors": [(255, 255, 0), (255, 165, 0), (255, 140, 0)], "keywords": ["light", "metal"]},
            "argan": {"colors": [(139, 69, 19), (160, 82, 45), (255, 228, 196)], "keywords": ["oil", "nut"]},
            "price_tags": {"colors": [(255, 255, 255), (255, 255, 224), (245, 245, 220)], "keywords": ["text", "number"]}
        }
    
    def analyze_colors(self, image):
        """Analyze dominant colors in image"""
        img_array = np.array(image)
        img_array = img_array.reshape(-1, 3)
        
        # Get dominant colors using k-means
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans.fit(img_array)
        colors = kmeans.cluster_centers_.astype(int)
        
        return colors
    
    def predict_from_base64(self, image_base64):
        """Predict using rule-based approach"""
        try:
            # Decode image
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data)).convert('RGB')
            
            # Analyze colors
            dominant_colors = self.analyze_colors(image)
            
            # Score each category
            scores = {}
            for category, features in self.categories.items():
                score = 0
                
                # Color matching
                for dom_color in dominant_colors:
                    for ref_color in features["colors"]:
                        # Calculate color distance
                        distance = np.sqrt(sum((dom_color - np.array(ref_color))**2))
                        if distance < 100:  # Threshold for color similarity
                            score += (100 - distance) / 100
                
                scores[category] = max(0.1, min(0.9, score / 3))  # Normalize
            
            # Ensure scores sum to reasonable values
            total = sum(scores.values())
            if total > 0:
                scores = {k: v/total for k, v in scores.items()}
            else:
                scores = {k: 1/len(self.categories) for k in self.categories}
            
            # Get prediction
            predicted_category = max(scores, key=scores.get)
            confidence = scores[predicted_category]
            
            # If confidence is reasonable, return it
            if confidence > 0.2:
                return {
                    "success": True,
                    "product_type": predicted_category,
                    "confidence": round(confidence, 3),
                    "all_predictions": {k: round(v, 3) for k, v in scores.items()}
                }
            else:
                # Low confidence - return top 3
                sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
                return {
                    "success": True,
                    "product_type": "uncertain",
                    "confidence": round(confidence, 3),
                    "message": f"Uncertain prediction. Top possibilities: {', '.join([f'{k} ({round(v, 3)})' for k, v in sorted_scores[:3]])}",
                    "top_suggestions": [{"category": k, "confidence": round(v, 3)} for k, v in sorted_scores[:3]],
                    "all_predictions": {k: round(v, 3) for k, v in scores.items()}
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# For compatibility
class ImprovedPriceClassifier(RuleBasedClassifier):
    pass

if __name__ == "__main__":
    classifier = RuleBasedClassifier()
    print("✅ Rule-based classifier ready")