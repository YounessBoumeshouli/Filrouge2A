import random

class AIService:
    @staticmethod
    def analyze_location(image_bytes: bytes) -> dict:
        # TODO: Integrate real AI model (YOLO/ResNet/Google Vision)
        # Mock response
        return {
            "name": "Hassan II Mosque",
            "city": "Casablanca",
            "description": "The Hassan II Mosque is a mosque in Casablanca, Morocco. It is the second largest functioning mosque in Africa and is the 7th largest in the world.",
            "history": "Completed in 1993, designed by Michel Pinseau and built by Bouygues under the guidance of King Hassan II.",
            "latitude": 33.6081,
            "longitude": -7.6324
        }

    @staticmethod
    def analyze_price(image_bytes: bytes) -> dict:
        # TODO: Integrate real AI model
        # Mock response
        return {
            "product_name": "Leather Babouche",
            "estimated_price_min": 70.0,
            "estimated_price_max": 150.0,
            "confidence_score": 0.88
        }
