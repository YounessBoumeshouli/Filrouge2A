#!/usr/bin/env python3
"""
Pinterest Image Scraper with Auto ChromeDriver Setup
===================================================

Automatically manages ChromeDriver and scrapes Pinterest images.
"""

import os
import time
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
from PIL import Image
import io

class PinterestScraperAuto:
    def __init__(self, headless=False):
        self.setup_driver(headless)
        
    def setup_driver(self, headless=False):
        """Setup Chrome driver with automatic ChromeDriver management"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            # Automatically download and setup ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to hide automation
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Chrome driver initialized successfully with auto-setup")
        except Exception as e:
            print(f"❌ Failed to initialize Chrome driver: {e}")
            raise
    
    def wait_and_scroll(self, scrolls=5):
        """Wait and scroll to load more images"""
        print("📜 Scrolling to load more images...")
        for i in range(scrolls):
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Scroll up a bit to trigger loading
            self.driver.execute_script("window.scrollBy(0, -500);")
            time.sleep(1)
            
            print(f"   Scroll {i+1}/{scrolls} completed")
    
    def get_pinterest_images(self, search_query, max_images=20):
        """Get image URLs from Pinterest search"""
        
        # Construct search URL
        encoded_query = urllib.parse.quote(search_query)
        url = f"https://www.pinterest.com/search/pins/?q={encoded_query}"
        
        print(f"🔍 Searching Pinterest for: {search_query}")
        print(f"🌐 URL: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(5)
            
            # Wait for images to load and scroll
            self.wait_and_scroll(scrolls=6)
            
            # Find image elements with multiple selectors
            image_selectors = [
                "img[src*='pinimg.com']",
                "img[data-test-id='pin-image']",
                "img[alt*='Pin']",
                "div[data-test-id='pin'] img"
            ]
            
            all_images = []
            for selector in image_selectors:
                images = self.driver.find_elements(By.CSS_SELECTOR, selector)
                all_images.extend(images)
            
            print(f"📸 Found {len(all_images)} total image elements")
            
            # Extract unique URLs
            image_urls = set()
            for img in all_images:
                try:
                    src = img.get_attribute('src')
                    if src and 'pinimg.com' in src and 'http' in src:
                        # Get higher resolution
                        if '/236x/' in src:
                            src = src.replace('/236x/', '/736x/')
                        elif '/474x/' in src:
                            src = src.replace('/474x/', '/736x/')
                        
                        image_urls.add(src)
                        
                        if len(image_urls) >= max_images:
                            break
                            
                except Exception as e:
                    continue
            
            image_urls = list(image_urls)[:max_images]
            print(f"✅ Collected {len(image_urls)} unique image URLs")
            
            return image_urls
            
        except Exception as e:
            print(f"❌ Error scraping Pinterest: {e}")
            return []
    
    def download_image(self, url, save_path):
        """Download and save image"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.pinterest.com/',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = requests.get(url, headers=headers, timeout=15, stream=True)
            response.raise_for_status()
            
            # Check if it's an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                print(f"⚠️ Not an image: {content_type}")
                return False
            
            # Process image
            img = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            
            # Resize if too large (optional)
            if img.width > 1024 or img.height > 1024:
                img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
            # Save as JPEG
            img.save(save_path, 'JPEG', quality=90, optimize=True)
            
            print(f"✅ Downloaded: {save_path.name} ({img.width}x{img.height})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {url[:50]}...: {e}")
            return False
    
    def scrape_images(self, search_query, output_folder, start_number=20, max_images=15):
        """Main scraping function"""
        
        # Create output directory
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"🎯 Target: {search_query}")
        print(f"📁 Output: {output_path}")
        print(f"🔢 Starting from: image_{start_number}.jpg")
        print(f"📊 Max images: {max_images}")
        print("-" * 60)
        
        # Get image URLs
        image_urls = self.get_pinterest_images(search_query, max_images * 2)
        
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
                time.sleep(2)  # Be respectful
            else:
                # Don't increment number if download failed
                continue
        
        print("-" * 60)
        print(f"🎉 Successfully downloaded {downloaded} images!")
        print(f"📁 Saved to: {output_path}")
        
        return downloaded
    
    def close(self):
        """Close browser"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("🔒 Browser closed")

def main():
    # Configuration
    SEARCH_QUERY = "Handcrafted Tamegroute Ceramic Cake Stand"
    OUTPUT_FOLDER = r"c:\Users\boume\Briefs\Filrouge2A\images\product_51_Handcrafted Tamegroute Ceramic Cake Stand with Sca"
    START_NUMBER = 20
    MAX_IMAGES = 15
    
    print("🏺 Pinterest Scraper for Ceramic Cake Stands")
    print("=" * 60)
    
    scraper = None
    try:
        # Initialize scraper
        print("🚀 Initializing scraper...")
        scraper = PinterestScraperAuto(headless=False)
        
        # Start scraping
        downloaded = scraper.scrape_images(
            search_query=SEARCH_QUERY,
            output_folder=OUTPUT_FOLDER,
            start_number=START_NUMBER,
            max_images=MAX_IMAGES
        )
        
        if downloaded > 0:
            print(f"\n✅ Mission accomplished!")
            print(f"📊 Downloaded: {downloaded} images")
            print(f"🏷️ Range: image_{START_NUMBER}.jpg to image_{START_NUMBER + downloaded - 1}.jpg")
            print(f"📁 Location: {OUTPUT_FOLDER}")
        else:
            print("\n❌ No images downloaded")
            
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    except Exception as e:
        print(f"\n💥 Error: {e}")
    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    main()