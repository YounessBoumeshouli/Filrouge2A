#!/usr/bin/env python3
"""
Simple Pinterest Image Scraper (No Selenium)
============================================

Downloads images from Pinterest using requests and basic HTML parsing.
"""

import os
import re
import json
import time
import requests
from pathlib import Path
from PIL import Image
import io
import urllib.parse

class SimplePinterestScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def search_pinterest(self, query, max_images=20):
        """Search Pinterest and extract image URLs"""
        
        # Encode the search query
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.pinterest.com/search/pins/?q={encoded_query}"
        
        print(f"🔍 Searching Pinterest: {query}")
        print(f"🌐 URL: {search_url}")
        
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            # Extract image URLs from the HTML
            html_content = response.text
            
            # Look for Pinterest image URLs in the HTML
            image_patterns = [
                r'https://i\.pinimg\.com/[^"\']*\.jpg',
                r'https://i\.pinimg\.com/[^"\']*\.jpeg',
                r'https://i\.pinimg\.com/[^"\']*\.png',
                r'https://i\.pinimg\.com/[^"\']*\.webp'
            ]
            
            image_urls = set()
            for pattern in image_patterns:
                matches = re.findall(pattern, html_content)
                for match in matches:
                    # Clean up the URL
                    clean_url = match.split('?')[0]  # Remove query parameters
                    
                    # Upgrade to higher resolution
                    if '/236x/' in clean_url:
                        clean_url = clean_url.replace('/236x/', '/736x/')
                    elif '/474x/' in clean_url:
                        clean_url = clean_url.replace('/474x/', '/736x/')
                    
                    image_urls.add(clean_url)
                    
                    if len(image_urls) >= max_images:
                        break
                
                if len(image_urls) >= max_images:
                    break
            
            image_urls = list(image_urls)[:max_images]
            print(f"✅ Found {len(image_urls)} image URLs")
            
            return image_urls
            
        except Exception as e:
            print(f"❌ Error searching Pinterest: {e}")
            return []
    
    def download_image(self, url, save_path):
        """Download image from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.pinterest.com/',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            }
            
            response = requests.get(url, headers=headers, timeout=15, stream=True)
            response.raise_for_status()
            
            # Verify content type
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"⚠️ Not an image: {content_type}")
                return False
            
            # Process image
            img = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            
            # Resize if too large
            if img.width > 1024 or img.height > 1024:
                img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
            # Save as JPEG
            img.save(save_path, 'JPEG', quality=90, optimize=True)
            
            print(f"✅ Downloaded: {save_path.name} ({img.width}x{img.height})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {url[:50]}...: {e}")
            return False
    
    def scrape_images(self, query, output_folder, start_number=20, max_images=15):
        """Main scraping function"""
        
        # Create output directory
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"🎯 Query: {query}")
        print(f"📁 Output: {output_path}")
        print(f"🔢 Starting from: image_{start_number}.jpg")
        print(f"📊 Max images: {max_images}")
        print("-" * 60)
        
        # Search for images
        image_urls = self.search_pinterest(query, max_images * 2)
        
        if not image_urls:
            print("❌ No images found!")
            return 0
        
        # Download images
        downloaded = 0
        current_num = start_number
        
        for i, url in enumerate(image_urls):
            if downloaded >= max_images:
                break
            
            save_path = output_path / f"image_{current_num}.jpg"
            
            # Skip existing files
            if save_path.exists():
                print(f"⏭️ Skipping image_{current_num}.jpg (exists)")
                current_num += 1
                continue
            
            print(f"📥 Downloading {i+1}/{len(image_urls)}: image_{current_num}.jpg")
            
            if self.download_image(url, save_path):
                downloaded += 1
                current_num += 1
                time.sleep(1)  # Be respectful
            else:
                continue
        
        print("-" * 60)
        print(f"🎉 Successfully downloaded {downloaded} images!")
        
        return downloaded

def main():
    # Configuration
    SEARCH_QUERY = "Handcrafted Tamegroute Ceramic Cake Stand"
    OUTPUT_FOLDER = r"c:\Users\boume\Briefs\Filrouge2A\images\product_51_Handcrafted Tamegroute Ceramic Cake Stand with Sca"
    START_NUMBER = 20
    MAX_IMAGES = 15
    
    print("🏺 Simple Pinterest Scraper for Ceramic Cake Stands")
    print("=" * 60)
    
    try:
        scraper = SimplePinterestScraper()
        
        downloaded = scraper.scrape_images(
            query=SEARCH_QUERY,
            output_folder=OUTPUT_FOLDER,
            start_number=START_NUMBER,
            max_images=MAX_IMAGES
        )
        
        if downloaded > 0:
            print(f"\n✅ Scraping completed!")
            print(f"📊 Downloaded: {downloaded} images")
            print(f"🏷️ Range: image_{START_NUMBER}.jpg to image_{START_NUMBER + downloaded - 1}.jpg")
            print(f"📁 Location: {OUTPUT_FOLDER}")
        else:
            print("\n❌ No images downloaded")
            
    except Exception as e:
        print(f"\n💥 Error: {e}")

if __name__ == "__main__":
    main()