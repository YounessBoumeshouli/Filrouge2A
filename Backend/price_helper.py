#!/usr/bin/env python3
"""
Ceramic Products Price Helper
============================

Price prediction system that works with the trained YOLO model to estimate
prices for detected ceramic products based on Marrakech souk market data.
"""

from typing import Dict
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
        # base_min = product_data["price_min_mad"]
        # base_max = product_data["price_max_mad"]
        
