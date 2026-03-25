#!/usr/bin/env python3
"""
Ceramic Products Price Helper
============================

Price prediction system that works with the trained YOLO model to estimate
prices for detected ceramic products based on Marrakech souk market data.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class PriceHelper:
    """
    Price prediction helper for ceramic products detected by YOLO model.
    Uses market data from Marrakech souks to estimate fair price ranges.
    """
    
    def __init__(self):
        """Initialize the price helper with ceramic product price data"""
        
        # Price data based on Marrakech souk market research
        # Prices in MAD (Moroccan Dirhams) - 1 EUR ≈ 11 MAD, 1 USD ≈ 10 MAD
        self.price_data = {
            # Class 0 - Ceramic Vase
            "Ceramic Vase": {
                "price_min_mad": 80,
                "price_max_mad": 300,
                "price_min_usd": 8,
                "price_max_usd": 30,
                "price_min_eur": 7,
                "price_max_eur": 27,
                "category": "decorative_ceramics",
                "souk_location": "Souk Semmarine / Chabi Chic",
                "notes": "Hand-painted ceramic vases. Price varies by size, design complexity, and craftsmanship quality.",
                "factors": {
                    "small": 0.7,      # 70% of base price for small items
                    "medium": 1.0,     # 100% base price
                    "large": 1.5,      # 150% for large items
                    "decorative": 1.3, # 130% for highly decorative pieces
                    "plain": 0.8       # 80% for plain/simple designs
                }
            },
            
            # Class 1 - Tagine
            "Tagine": {
                "price_min_mad": 50,
                "price_max_mad": 200,
                "price_min_usd": 5,
                "price_max_usd": 20,
                "price_min_eur": 4,
                "price_max_eur": 18,
                "category": "functional_ceramics",
                "souk_location": "Souk Semmarine / Rahba Kedima",
                "notes": "Traditional Moroccan cooking pot. Functional tagines cost less than decorative ones.",
                "factors": {
                    "small": 0.6,
                    "medium": 1.0,
                    "large": 1.4,
                    "decorative": 1.6,
                    "functional": 0.9
                }
            },
            
            # Class 2 - Ceramic Cups
            "Ceramic Cups": {
                "price_min_mad": 30,
                "price_max_mad": 120,
                "price_min_usd": 3,
                "price_max_usd": 12,
                "price_min_eur": 3,
                "price_max_eur": 11,
                "category": "functional_ceramics",
                "souk_location": "Souk Semmarine",
                "notes": "Traditional Moroccan tea glasses and ceramic cups. Often sold in sets.",
                "factors": {
                    "single": 1.0,
                    "set": 0.8,        # 20% discount for sets
                    "decorative": 1.2,
                    "plain": 0.9
                }
            },
            
            # Class 3 - Handcrafted Tamegroute Ceramic Cake Stand
            "Handcrafted Tamegroute Ceramic Cake Stand": {
                "price_min_mad": 150,
                "price_max_mad": 400,
                "price_min_usd": 15,
                "price_max_usd": 40,
                "price_min_eur": 14,
                "price_max_eur": 36,
                "category": "premium_ceramics",
                "souk_location": "Chabi Chic / Premium ceramic shops",
                "notes": "Tamegroute ceramics are premium handcrafted pieces with distinctive green glaze.",
                "factors": {
                    "small": 0.8,
                    "medium": 1.0,
                    "large": 1.3,
                    "authentic_tamegroute": 1.4,
                    "replica": 0.7
                }
            },
            
            # Class 4 - White Ceramic Divided Plate with Silver Accents
            "White Ceramic Divided Plate with Silver Accents": {
                "price_min_mad": 100,
                "price_max_mad": 250,
                "price_min_usd": 10,
                "price_max_usd": 25,
                "price_min_eur": 9,
                "price_max_eur": 23,
                "category": "decorative_ceramics",
                "souk_location": "Chabi Chic / Upscale ceramic shops",
                "notes": "Elegant serving plates with metallic accents. Premium decorative pieces.",
                "factors": {
                    "small": 0.9,
                    "medium": 1.0,
                    "large": 1.2,
                    "silver_accents": 1.3,
                    "gold_accents": 1.5,
                    "plain": 0.8
                }
            },
            
            # Class 5 - Tamegroute Ceramic Pitcher
            "Tamegroute Ceramic Pitcher Handmade Moroccan Water": {
                "price_min_mad": 120,
                "price_max_mad": 350,
                "price_min_usd": 12,
                "price_max_usd": 35,
                "price_min_eur": 11,
                "price_max_eur": 32,
                "category": "premium_ceramics",
                "souk_location": "Chabi Chic / Tamegroute ceramic specialists",
                "notes": "Authentic Tamegroute water pitchers with traditional green glaze. Functional and decorative.",
                "factors": {
                    "small": 0.8,
                    "medium": 1.0,
                    "large": 1.3,
                    "authentic_tamegroute": 1.4,
                    "functional": 0.9,
                    "decorative": 1.2
                }
            }
        }
        
        # Currency conversion rates (approximate)
        self.currency_rates = {
            "MAD": 1.0,
            "USD": 0.1,    # 1 MAD ≈ 0.1 USD
            "EUR": 0.09    # 1 MAD ≈ 0.09 EUR
        }
        
        logger.info("PriceHelper initialized with ceramic product price data")
    
    def get_price_estimate(self, class_name: str, confidence: float = 1.0, 
                          size_factor: str = "medium", currency: str = "USD") -> Dict:
        """
        Get price estimate for a detected ceramic product.
        
        Args:
            class_name: Name of the detected class
            confidence: Detection confidence (0.0-1.0)
            size_factor: Size estimation ("small", "medium", "large")
            currency: Target currency ("MAD", "USD", "EUR")
            
        Returns:
            Dictionary with price estimate and metadata
        """
        
        if class_name not in self.price_data:
            return {
                "success": False,
                "error": f"No price data available for class: {class_name}",
                "class_name": class_name
            }
        
        product_data = self.price_data[class_name]
        
        # Get base price range in MAD
        base_min = product_data["price_min_mad"]
        base_max = product_data["price_max_mad"]
        
        # Apply size factor if available\n        size_multiplier = product_data.get("factors", {}).get(size_factor, 1.0)\n        \n        # Apply confidence factor (lower confidence = wider price range)\n        confidence_factor = max(0.7, confidence)  # Minimum 70% confidence factor\n        \n        # Calculate adjusted prices in MAD\n        adjusted_min = base_min * size_multiplier * confidence_factor\n        adjusted_max = base_max * size_multiplier / confidence_factor\n        \n        # Convert to target currency\n        if currency.upper() in self.currency_rates:\n            rate = self.currency_rates[currency.upper()]\n            final_min = adjusted_min * rate\n            final_max = adjusted_max * rate\n        else:\n            # Default to MAD if currency not supported\n            currency = "MAD"\n            final_min = adjusted_min\n            final_max = adjusted_max\n        \n        return {\n            "success": True,\n            "class_name": class_name,\n            "category": product_data["category"],\n            "price_range": {\n                "min": round(final_min, 2),\n                "max": round(final_max, 2),\n                "currency": currency.upper(),\n                "formatted": f"{final_min:.0f}-{final_max:.0f} {currency.upper()}\"\n            },\n            "base_price_mad": {\n                "min": base_min,\n                "max": base_max\n            },\n            "factors_applied": {\n                "size_factor": size_factor,\n                "size_multiplier": size_multiplier,\n                "confidence": confidence,\n                "confidence_factor": confidence_factor\n            },\n            "market_info": {\n                "souk_location": product_data["souk_location"],\n                "notes": product_data["notes"]\n            }\n        }\n    \n    def get_batch_price_estimates(self, detections: List[Dict], currency: str = "USD") -> List[Dict]:\n        \"\"\"\n        Get price estimates for multiple detections.\n        \n        Args:\n            detections: List of detection dictionaries from YOLO\n            currency: Target currency\n            \n        Returns:\n            List of price estimates\n        \"\"\"\n        \n        estimates = []\n        \n        for detection in detections:\n            class_name = detection.get(\"class_name\", \"\")\n            confidence = detection.get(\"confidence\", 1.0)\n            \n            # Estimate size based on bounding box area (if available)\n            bbox = detection.get(\"bbox\", {})\n            size_factor = self._estimate_size_from_bbox(bbox)\n            \n            estimate = self.get_price_estimate(\n                class_name=class_name,\n                confidence=confidence,\n                size_factor=size_factor,\n                currency=currency\n            )\n            \n            # Add detection info to estimate\n            if estimate[\"success\"]:\n                estimate[\"detection_info\"] = {\n                    \"confidence\": confidence,\n                    \"bbox\": bbox,\n                    \"estimated_size\": size_factor\n                }\n            \n            estimates.append(estimate)\n        \n        return estimates\n    \n    def _estimate_size_from_bbox(self, bbox: Dict) -> str:\n        \"\"\"\n        Estimate product size based on bounding box dimensions.\n        \n        Args:\n            bbox: Bounding box dictionary with width/height\n            \n        Returns:\n            Size category: \"small\", \"medium\", or \"large\"\n        \"\"\"\n        \n        if not bbox or \"width\" not in bbox or \"height\" not in bbox:\n            return \"medium\"  # Default\n        \n        # Calculate area as percentage of image\n        area = bbox[\"width\"] * bbox[\"height\"]\n        \n        # Thresholds for size classification (adjust based on your data)\n        if area < 10000:  # Small objects\n            return \"small\"\n        elif area > 50000:  # Large objects\n            return \"large\"\n        else:\n            return \"medium\"\n    \n    def get_market_summary(self) -> Dict:\n        \"\"\"\n        Get summary of all available products and their price ranges.\n        \n        Returns:\n            Market summary dictionary\n        \"\"\"\n        \n        summary = {\n            \"total_products\": len(self.price_data),\n            \"categories\": {},\n            \"price_ranges\": {},\n            \"currency_info\": {\n                \"base_currency\": \"MAD\",\n                \"supported_currencies\": list(self.currency_rates.keys()),\n                \"conversion_rates\": self.currency_rates\n            }\n        }\n        \n        # Group by category\n        for product_name, data in self.price_data.items():\n            category = data[\"category\"]\n            if category not in summary[\"categories\"]:\n                summary[\"categories\"][category] = []\n            summary[\"categories\"][category].append(product_name)\n            \n            # Price ranges in different currencies\n            summary[\"price_ranges\"][product_name] = {\n                \"MAD\": f\"{data['price_min_mad']}-{data['price_max_mad']}\",\n                \"USD\": f\"{data['price_min_usd']}-{data['price_max_usd']}\",\n                \"EUR\": f\"{data['price_min_eur']}-{data['price_max_eur']}\"\n            }\n        \n        return summary\n    \n    def save_price_data(self, filepath: str) -> bool:\n        \"\"\"\n        Save price data to JSON file.\n        \n        Args:\n            filepath: Path to save the JSON file\n            \n        Returns:\n            True if successful, False otherwise\n        \"\"\"\n        \n        try:\n            data = {\n                \"price_data\": self.price_data,\n                \"currency_rates\": self.currency_rates,\n                \"metadata\": {\n                    \"source\": \"Marrakech Souk Market Research\",\n                    \"note\": \"Prices are estimates based on market research. Actual prices may vary.\",\n                    \"last_updated\": \"2024-03\"\n                }\n            }\n            \n            with open(filepath, 'w', encoding='utf-8') as f:\n                json.dump(data, f, indent=2, ensure_ascii=False)\n            \n            logger.info(f\"Price data saved to {filepath}\")\n            return True\n            \n        except Exception as e:\n            logger.error(f\"Failed to save price data: {e}\")\n            return False\n    \n    def load_price_data(self, filepath: str) -> bool:\n        \"\"\"\n        Load price data from JSON file.\n        \n        Args:\n            filepath: Path to the JSON file\n            \n        Returns:\n            True if successful, False otherwise\n        \"\"\"\n        \n        try:\n            with open(filepath, 'r', encoding='utf-8') as f:\n                data = json.load(f)\n            \n            if \"price_data\" in data:\n                self.price_data = data[\"price_data\"]\n            if \"currency_rates\" in data:\n                self.currency_rates = data[\"currency_rates\"]\n            \n            logger.info(f\"Price data loaded from {filepath}\")\n            return True\n            \n        except Exception as e:\n            logger.error(f\"Failed to load price data: {e}\")\n            return False\n\n\n# Example usage and testing\nif __name__ == \"__main__\":\n    # Initialize price helper\n    price_helper = PriceHelper()\n    \n    # Test single price estimate\n    print(\"=\" * 60)\n    print(\"CERAMIC PRODUCTS PRICE HELPER - TEST\")\n    print(\"=\" * 60)\n    \n    # Test each product class\n    test_classes = [\n        \"Ceramic Vase\",\n        \"Tagine\",\n        \"Ceramic Cups\",\n        \"Handcrafted Tamegroute Ceramic Cake Stand\",\n        \"White Ceramic Divided Plate with Silver Accents\",\n        \"Tamegroute Ceramic Pitcher Handmade Moroccan Water\"\n    ]\n    \n    for class_name in test_classes:\n        print(f\"\\n📦 {class_name}:\")\n        \n        # Test different currencies\n        for currency in [\"USD\", \"EUR\", \"MAD\"]:\n            estimate = price_helper.get_price_estimate(\n                class_name=class_name,\n                confidence=0.85,\n                size_factor=\"medium\",\n                currency=currency\n            )\n            \n            if estimate[\"success\"]:\n                price_range = estimate[\"price_range\"]\n                print(f\"  {currency}: {price_range['formatted']}\")\n    \n    # Test batch processing\n    print(\"\\n\" + \"=\" * 60)\n    print(\"BATCH PROCESSING TEST\")\n    print(\"=\" * 60)\n    \n    sample_detections = [\n        {\n            \"class_name\": \"Ceramic Vase\",\n            \"confidence\": 0.92,\n            \"bbox\": {\"width\": 150, \"height\": 200, \"x1\": 100, \"y1\": 50, \"x2\": 250, \"y2\": 250}\n        },\n        {\n            \"class_name\": \"Tagine\",\n            \"confidence\": 0.78,\n            \"bbox\": {\"width\": 300, \"height\": 250, \"x1\": 50, \"y1\": 100, \"x2\": 350, \"y2\": 350}\n        }\n    ]\n    \n    batch_estimates = price_helper.get_batch_price_estimates(sample_detections, currency=\"USD\")\n    \n    for i, estimate in enumerate(batch_estimates):\n        if estimate[\"success\"]:\n            print(f\"\\nDetection {i+1}: {estimate['class_name']}\")\n            print(f\"  Price: {estimate['price_range']['formatted']}\")\n            print(f\"  Confidence: {estimate['detection_info']['confidence']:.2f}\")\n            print(f\"  Size: {estimate['detection_info']['estimated_size']}\")\n    \n    # Market summary\n    print(\"\\n\" + \"=\" * 60)\n    print(\"MARKET SUMMARY\")\n    print(\"=\" * 60)\n    \n    summary = price_helper.get_market_summary()\n    print(f\"Total products: {summary['total_products']}\")\n    print(f\"Categories: {list(summary['categories'].keys())}\")\n    print(f\"Supported currencies: {summary['currency_info']['supported_currencies']}\")\n