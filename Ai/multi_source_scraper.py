#!/usr/bin/env python3
"""
Multi-Source Image Scraper for Ceramic Products
===============================================

Downloads images from multiple sources including direct URLs.
Provides manual download functionality when automated scraping fails.
"""

import os
import requests
import time
from pathlib import Path
from PIL import Image
import io
import json

class MultiSourceImageScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
    
    def download_from_url(self, url, save_path):
        """Download image from direct URL"""
        try:
            response = self.session.get(url, timeout=15, stream=True)
            response.raise_for_status()
            
            # Check content type
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
    
    def download_from_urls(self, urls, output_folder, start_number=20):
        """Download images from a list of URLs"""
        
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        downloaded = 0
        current_num = start_number
        
        for i, url in enumerate(urls):
            save_path = output_path / f"image_{current_num}.jpg"
            
            # Skip existing files
            if save_path.exists():
                print(f"⏭️ Skipping image_{current_num}.jpg (exists)")
                current_num += 1
                continue
            
            print(f"📥 Downloading {i+1}/{len(urls)}: image_{current_num}.jpg")
            
            if self.download_from_url(url, save_path):
                downloaded += 1
                current_num += 1
                time.sleep(1)
            else:
                continue
        
        return downloaded
    
    def create_manual_download_script(self, output_folder, start_number=20):
        """Create a script for manual image downloading"""
        
        script_content = f'''#!/usr/bin/env python3
"""
Manual Image Downloader
======================

Paste image URLs below and run this script to download them.
"""

import requests
from pathlib import Path
from PIL import Image
import io

# PASTE YOUR IMAGE URLs HERE (one per line)
IMAGE_URLS = [
    # Example URLs - replace with actual Pinterest image URLs
    # "https://i.pinimg.com/736x/xx/xx/xx/xxxxxx.jpg",
    # "https://i.pinimg.com/736x/yy/yy/yy/yyyyyy.jpg",
    # Add more URLs here...
]

def download_image(url, save_path):
    try:
        headers = {{
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.pinterest.com/',
        }}
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        img = Image.open(io.BytesIO(response.content))
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        
        img.save(save_path, 'JPEG', quality=90)
        print(f"✅ Downloaded: {{save_path.name}}")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {{e}}")
        return False

def main():
    output_folder = Path(r"{output_folder}")
    output_folder.mkdir(parents=True, exist_ok=True)
    
    if not IMAGE_URLS or all(url.startswith('#') or not url.strip() for url in IMAGE_URLS):
        print("❌ No URLs provided!")
        print("Please edit this script and add image URLs to the IMAGE_URLS list.")
        return
    
    downloaded = 0
    current_num = {start_number}
    
    for url in IMAGE_URLS:
        url = url.strip()
        if not url or url.startswith('#'):
            continue
            
        save_path = output_folder / f"image_{{current_num}}.jpg"
        
        if save_path.exists():
            print(f"⏭️ Skipping image_{{current_num}}.jpg (exists)")
            current_num += 1
            continue
        
        if download_image(url, save_path):
            downloaded += 1
            current_num += 1
    
    print(f"\\n🎉 Downloaded {{downloaded}} images to {{output_folder}}")

if __name__ == "__main__":
    main()
'''
        
        script_path = Path(output_folder) / "manual_downloader.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        print(f"📝 Created manual download script: {script_path}")
        return script_path

def create_sample_urls():
    """Create sample Pinterest URLs for ceramic cake stands"""
    
    # These are example Pinterest image URLs for ceramic cake stands
    # In practice, you would get these by manually browsing Pinterest
    sample_urls = [
        "https://i.pinimg.com/736x/8a/2f/3d/8a2f3d4c5e6f7a8b9c0d1e2f3a4b5c6d.jpg",
        "https://i.pinimg.com/736x/1b/3c/5d/1b3c5d7e9f0a1b2c3d4e5f6a7b8c9d0e.jpg",
        "https://i.pinimg.com/736x/2c/4d/6e/2c4d6e8f0a1b2c3d4e5f6a7b8c9d0e1f.jpg",
        # Add more URLs as needed
    ]
    
    return sample_urls

def main():
    # Configuration
    OUTPUT_FOLDER = r"c:\Users\boume\Briefs\Filrouge2A\images\product_51_Handcrafted Tamegroute Ceramic Cake Stand with Sca"
    START_NUMBER = 20
    
    print("🏺 Multi-Source Image Scraper for Ceramic Cake Stands")
    print("=" * 60)
    
    scraper = MultiSourceImageScraper()
    
    # Create manual download script
    script_path = scraper.create_manual_download_script(OUTPUT_FOLDER, START_NUMBER)
    
    print(f"\\n📋 MANUAL DOWNLOAD INSTRUCTIONS:")
    print(f"1. Open Pinterest in your browser")
    print(f"2. Search for: 'Handcrafted Tamegroute Ceramic Cake Stand'")
    print(f"3. Right-click on images and copy image URLs")
    print(f"4. Edit the script: {script_path}")
    print(f"5. Paste the URLs in the IMAGE_URLS list")
    print(f"6. Run: python {script_path.name}")
    
    print(f"\\n🔗 Pinterest Search URL:")
    print(f"https://www.pinterest.com/search/pins/?q=Handcrafted%20Tamegroute%20Ceramic%20Cake%20Stand")
    
    print(f"\\n💡 TIP: Look for high-resolution images (736x or larger)")
    print(f"Right-click → 'Copy image address' to get the direct URL")
    
    # Try with sample URLs (if available)
    sample_urls = create_sample_urls()
    if sample_urls:
        print(f"\\n🧪 Testing with sample URLs...")
        downloaded = scraper.download_from_urls(sample_urls, OUTPUT_FOLDER, START_NUMBER)
        if downloaded > 0:
            print(f"✅ Downloaded {downloaded} sample images")
        else:
            print("❌ Sample URLs didn't work (expected)")

if __name__ == "__main__":
    main()