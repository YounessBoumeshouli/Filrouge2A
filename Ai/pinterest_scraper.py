#!/usr/bin/env python3
"""
Pinterest Image Scraper for Product Dataset
==========================================

Scrapes images from Pinterest for a specific product and saves them
in the appropriate folder with sequential naming.
"""

import os
import time
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import urllib.parse
from PIL import Image
import io

class PinterestScraper:
    def __init__(self, headless=True):
        self.setup_driver(headless)
        
    def setup_driver(self, headless=True):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Chrome driver initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Chrome driver: {e}")
            print("Please make sure ChromeDriver is installed and in PATH")
            raise
    
    def scroll_page(self, scrolls=3):
        """Scroll page to load more images"""
        for i in range(scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            print(f"Scrolled {i+1}/{scrolls} times")
    
    def get_image_urls(self, pinterest_url, max_images=20):
        """Extract image URLs from Pinterest search results"""
        print(f"🔍 Accessing Pinterest URL: {pinterest_url}")
        
        try:
            self.driver.get(pinterest_url)
            time.sleep(5)
            
            # Scroll to load more images
            self.scroll_page(scrolls=5)
            
            # Find all image elements
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, "img[src*='pinimg.com']")
            print(f"Found {len(image_elements)} image elements")
            
            image_urls = []
            for img in image_elements[:max_images]:
                try:
                    src = img.get_attribute('src')
                    if src and 'pinimg.com' in src:
                        # Get higher resolution version
                        if '/236x/' in src:
                            src = src.replace('/236x/', '/736x/')
                        elif '/474x/' in src:
                            src = src.replace('/474x/', '/736x/')
                        
                        if src not in image_urls:
                            image_urls.append(src)
                            print(f"📸 Found image URL: {src[:80]}...")
                            
                except Exception as e:
                    print(f"⚠️ Error extracting URL from image: {e}")
                    continue
            
            print(f"✅ Collected {len(image_urls)} unique image URLs")
            return image_urls
            
        except Exception as e:
            print(f"❌ Error accessing Pinterest: {e}")
            return []
    
    def download_image(self, url, save_path):
        """Download image from URL and save to path"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://www.pinterest.com/'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Verify it's an image
            try:
                img = Image.open(io.BytesIO(response.content))
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Save as JPEG
                img.save(save_path, 'JPEG', quality=95)
                print(f"✅ Downloaded: {save_path.name}")
                return True
                
            except Exception as e:
                print(f"⚠️ Invalid image format: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to download {url}: {e}")
            return False
    
    def scrape_pinterest(self, search_query, output_folder, start_number=20, max_images=20):
        """Main scraping function"""
        
        # Create output folder
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Construct Pinterest search URL
        encoded_query = urllib.parse.quote(search_query)
        pinterest_url = f"https://www.pinterest.com/search/pins/?q={encoded_query}&rs=typed"
        
        print(f"🎯 Scraping Pinterest for: {search_query}")
        print(f"📁 Output folder: {output_path}")
        print(f"🔢 Starting from image_{start_number}.jpg")
        
        # Get image URLs
        image_urls = self.get_image_urls(pinterest_url, max_images * 2)  # Get more URLs than needed
        
        if not image_urls:
            print("❌ No images found!")
            return 0
        
        # Download images
        downloaded_count = 0
        current_number = start_number
        
        for url in image_urls:
            if downloaded_count >= max_images:
                break
                
            save_path = output_path / f"image_{current_number}.jpg"
            
            # Skip if file already exists
            if save_path.exists():
                print(f"⏭️ Skipping {save_path.name} (already exists)")
                current_number += 1
                continue
            
            if self.download_image(url, save_path):
                downloaded_count += 1
                current_number += 1
                time.sleep(1)  # Be respectful to the server
            else:
                # If download failed, try next URL without incrementing number
                continue
        
        print(f"🎉 Successfully downloaded {downloaded_count} images!")
        return downloaded_count
    
    def close(self):
        """Close the browser driver"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("🔒 Browser closed")

def main():
    # Configuration
    SEARCH_QUERY = "Handcrafted Tamegroute Ceramic Cake Stand"
    OUTPUT_FOLDER = r"c:\Users\boume\Briefs\Filrouge2A\images\product_51_Handcrafted Tamegroute Ceramic Cake Stand with Sca"
    START_NUMBER = 20  # Start from image_20.jpg
    MAX_IMAGES = 15    # Download 15 new images
    
    print("🏺 Pinterest Image Scraper for Ceramic Cake Stands")
    print("=" * 60)
    
    scraper = None
    try:
        # Initialize scraper
        scraper = PinterestScraper(headless=False)  # Set to True for headless mode
        
        # Start scraping
        downloaded = scraper.scrape_pinterest(
            search_query=SEARCH_QUERY,
            output_folder=OUTPUT_FOLDER,
            start_number=START_NUMBER,
            max_images=MAX_IMAGES
        )
        
        if downloaded > 0:
            print(f"\n✅ Scraping completed successfully!")
            print(f"📊 Downloaded {downloaded} new images")
            print(f"📁 Images saved to: {OUTPUT_FOLDER}")
            print(f"🏷️ Files named: image_{START_NUMBER}.jpg to image_{START_NUMBER + downloaded - 1}.jpg")
        else:
            print("\n❌ No images were downloaded")
            
    except KeyboardInterrupt:
        print("\n⏹️ Scraping interrupted by user")
    except Exception as e:
        print(f"\n💥 Scraping failed: {e}")
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    main()