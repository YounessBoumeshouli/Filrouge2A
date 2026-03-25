#!/usr/bin/env python3
"""
Enhanced image scraper for Marrakech souk products
Scrapes images from multiple sources to build a larger dataset
"""

import os
import requests
import time
import json
from urllib.parse import quote
import hashlib
from PIL import Image
import io

class ImageScraper:
    def __init__(self, output_dir="../../marrakech_dataset_enhanced"):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Product categories with enhanced search terms
        self.categories = {
            "argan": [
                "argan oil morocco", "moroccan argan products", "argan nuts morocco",
                "argan oil bottle morocco", "moroccan argan cosmetics", "argan tree morocco",
                "traditional argan oil", "berber argan oil", "moroccan argan soap"
            ],
            "crafts": [
                "moroccan handicrafts", "marrakech crafts", "moroccan pottery",
                "moroccan ceramics", "traditional moroccan crafts", "berber crafts",
                "moroccan woodwork", "moroccan metalwork", "handmade morocco crafts"
            ],
            "jewelry": [
                "moroccan jewelry", "berber jewelry", "moroccan silver jewelry",
                "traditional moroccan jewelry", "moroccan gold jewelry", "tuareg jewelry",
                "moroccan necklace", "moroccan bracelet", "moroccan earrings"
            ],
            "lanterns": [
                "moroccan lanterns", "moroccan lamps", "traditional moroccan lighting",
                "moroccan metal lanterns", "marrakech lanterns", "moroccan brass lamps",
                "moroccan pendant lights", "moroccan table lamps", "berber lanterns"
            ],
            "leather": [
                "moroccan leather goods", "moroccan leather bags", "moroccan babouche",
                "moroccan leather slippers", "traditional moroccan leather", "moroccan poufs",
                "moroccan leather jackets", "moroccan leather belts", "fez leather goods"
            ],
            "price_tags": [
                "moroccan price tags", "souk price labels", "market price tags morocco",
                "moroccan shop prices", "bazaar price tags", "moroccan market labels",
                "handwritten price tags morocco", "arabic price tags", "dirham price tags"
            ],
            "spices": [
                "moroccan spices", "ras el hanout", "moroccan spice market",
                "traditional moroccan spices", "moroccan spice blend", "marrakech spices",
                "moroccan saffron", "moroccan cumin", "moroccan spice shop"
            ],
            "textiles": [
                "moroccan textiles", "moroccan fabrics", "berber textiles",
                "moroccan carpets", "moroccan rugs", "traditional moroccan textiles",
                "moroccan blankets", "moroccan scarves", "moroccan kilim"
            ]
        }
    
    def create_directories(self):
        """Create directory structure for scraped images"""
        for category in self.categories.keys():
            for source in ['bing', 'google', 'unsplash']:
                dir_path = os.path.join(self.output_dir, category, source)
                os.makedirs(dir_path, exist_ok=True)
    
    def get_image_hash(self, image_data):
        """Generate hash for image to avoid duplicates"""
        return hashlib.md5(image_data).hexdigest()
    
    def download_image(self, url, filepath):
        """Download and save image"""
        try:
            response = self.session.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Check if it's actually an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return False
            
            image_data = response.content
            
            # Validate image
            try:
                img = Image.open(io.BytesIO(image_data))
                # Skip very small images
                if img.size[0] < 100 or img.size[1] < 100:
                    return False
                
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Save image
                img.save(filepath, 'JPEG', quality=85)
                return True
                
            except Exception as e:
                print(f"Image validation failed: {e}")
                return False
                
        except Exception as e:
            print(f"Download failed for {url}: {e}")
            return False
    
    def scrape_bing_images(self, query, category, max_images=100):
        """Scrape images from Bing"""
        print(f"🔍 Scraping Bing for '{query}'...")
        
        base_url = "https://www.bing.com/images/search"
        params = {
            'q': query,
            'form': 'HDRSC2',
            'first': 1,
            'count': 35
        }
        
        downloaded = 0
        page = 0
        
        while downloaded < max_images and page < 5:  # Max 5 pages
            params['first'] = page * 35 + 1
            
            try:
                response = self.session.get(base_url, params=params, timeout=15)
                response.raise_for_status()
                
                # Simple extraction of image URLs from Bing response
                content = response.text
                
                # Look for image URLs in the response
                import re
                img_urls = re.findall(r'"murl":"([^"]+)"', content)
                
                if not img_urls:
                    break
                
                for i, url in enumerate(img_urls[:35]):  # Limit per page
                    if downloaded >= max_images:
                        break
                    
                    try:
                        # Clean URL
                        url = url.replace('\\u0026', '&')
                        
                        filename = f"bing_{downloaded:06d}.jpg"
                        filepath = os.path.join(self.output_dir, category, 'bing', filename)
                        
                        if self.download_image(url, filepath):
                            downloaded += 1
                            print(f"  ✅ Downloaded {downloaded}/{max_images}")
                        
                        time.sleep(0.5)  # Rate limiting
                        
                    except Exception as e:
                        print(f"  ❌ Error downloading image: {e}")
                        continue
                
                page += 1
                time.sleep(2)  # Rate limiting between pages
                
            except Exception as e:
                print(f"Error scraping Bing page {page}: {e}")
                break
        
        print(f"  📊 Downloaded {downloaded} images from Bing for {category}")
        return downloaded
    
    def scrape_unsplash_images(self, query, category, max_images=50):
        """Scrape images from Unsplash API"""
        print(f"🔍 Scraping Unsplash for '{query}'...")
        
        # Note: This requires Unsplash API key for production use
        # For demo purposes, using search endpoint
        base_url = "https://unsplash.com/napi/search/photos"
        
        downloaded = 0
        page = 1
        
        while downloaded < max_images and page <= 3:
            params = {
                'query': query,
                'page': page,
                'per_page': 20
            }
            
            try:
                response = self.session.get(base_url, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    if not results:
                        break
                    
                    for photo in results:
                        if downloaded >= max_images:
                            break
                        
                        try:
                            # Get regular size image URL
                            img_url = photo['urls']['regular']
                            
                            filename = f"unsplash_{downloaded:06d}.jpg"
                            filepath = os.path.join(self.output_dir, category, 'unsplash', filename)
                            
                            if self.download_image(img_url, filepath):
                                downloaded += 1
                                print(f"  ✅ Downloaded {downloaded}/{max_images}")
                            
                            time.sleep(1)  # Rate limiting
                            
                        except Exception as e:
                            print(f"  ❌ Error downloading Unsplash image: {e}")
                            continue
                
                page += 1
                time.sleep(2)
                
            except Exception as e:
                print(f"Error scraping Unsplash page {page}: {e}")
                break
        
        print(f"  📊 Downloaded {downloaded} images from Unsplash for {category}")
        return downloaded
    
    def scrape_category(self, category, images_per_source=100):
        """Scrape images for a specific category"""
        print(f"\n🎯 Scraping category: {category}")
        print("=" * 50)
        
        search_terms = self.categories[category]
        total_downloaded = 0
        
        # Scrape from Bing with multiple search terms
        bing_downloaded = 0
        for term in search_terms[:3]:  # Use first 3 terms for Bing
            downloaded = self.scrape_bing_images(term, category, images_per_source // 3)
            bing_downloaded += downloaded
            time.sleep(3)  # Rate limiting between terms
        
        # Scrape from Unsplash with selected terms
        unsplash_downloaded = 0
        for term in search_terms[:2]:  # Use first 2 terms for Unsplash
            downloaded = self.scrape_unsplash_images(term, category, 25)
            unsplash_downloaded += downloaded
            time.sleep(3)
        
        total_downloaded = bing_downloaded + unsplash_downloaded
        
        print(f"\n📊 Category '{category}' summary:")
        print(f"  Bing: {bing_downloaded} images")
        print(f"  Unsplash: {unsplash_downloaded} images")
        print(f"  Total: {total_downloaded} images")
        
        return total_downloaded
    
    def scrape_all_categories(self, images_per_source=100):
        """Scrape images for all categories"""
        print("🚀 Starting comprehensive image scraping")
        print("=" * 60)
        
        self.create_directories()
        
        total_images = 0
        results = {}
        
        for category in self.categories.keys():
            try:
                downloaded = self.scrape_category(category, images_per_source)
                results[category] = downloaded
                total_images += downloaded
                
                # Save progress
                with open(os.path.join(self.output_dir, 'scraping_progress.json'), 'w') as f:
                    json.dump(results, f, indent=2)
                
                print(f"\n⏸️  Pausing 10 seconds before next category...")
                time.sleep(10)
                
            except Exception as e:
                print(f"❌ Error scraping category {category}: {e}")
                results[category] = 0
                continue
        
        print("\n" + "=" * 60)
        print("🎉 Scraping Complete!")
        print("=" * 60)
        
        for category, count in results.items():
            print(f"  {category}: {count} images")
        
        print(f"\n📊 Total images scraped: {total_images}")
        
        # Save final results
        with open(os.path.join(self.output_dir, 'scraping_results.json'), 'w') as f:
            json.dump({
                'results': results,
                'total_images': total_images,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=2)
        
        return results

def main():
    scraper = ImageScraper()
    
    print("Enhanced Image Scraper for Marrakech Souk Products")
    print("=" * 60)
    
    # Scrape all categories
    results = scraper.scrape_all_categories(images_per_source=150)
    
    print("\n✅ Scraping completed!")
    print("Next steps:")
    print("1. Review scraped images and remove irrelevant ones")
    print("2. Run data preparation: python prepare_price_data.py")
    print("3. Train model with new data: python pipeline.py")

if __name__ == "__main__":
    main()