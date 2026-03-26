import requests
# from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin, urlparse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class MoroccanCeramicScraper:
    def __init__(self):
        self.base_url = "https://www.marrakeche.com"
        self.ceramic_url = "https://www.marrakeche.com/moroccan-ceramic"
        self.products = []
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Remove this line if you want to see the browser
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Please make sure ChromeDriver is installed and in PATH")
            raise
    
    def scrape_product_list(self):
        """Scrape the main ceramic page to get product links"""
        print("Scraping product list...")
        
        try:
            self.driver.get(self.ceramic_url)
            time.sleep(3)
            
            # Wait for products to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='ceramic'], .product-link, .product-item a"))
            )
            
            # Find product links - adjust selectors based on actual HTML structure
            product_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='ceramic'], .product-link, .product-item a, .grid-item a")
            
            product_urls = []
            for link in product_links:
                href = link.get_attribute('href')
                if href and 'ceramic' in href.lower():
                    full_url = urljoin(self.base_url, href)
                    if full_url not in product_urls:
                        product_urls.append(full_url)
            
            print(f"Found {len(product_urls)} product URLs")
            return product_urls
            
        except Exception as e:
            print(f"Error scraping product list: {e}")
            return []
    
    def scrape_product_details(self, product_url):
        """Scrape individual product page for details and images"""
        print(f"Scraping product: {product_url}")
        
        try:
            self.driver.get(product_url)
            time.sleep(2)
            
            # Extract product information
            product_data = {
                'url': product_url,
                'title': '',
                'description': '',
                'price': '',
                'images': []
            }
            
            # Get title
            try:
                title_element = self.driver.find_element(By.CSS_SELECTOR, "h1, .product-title, .title")
                product_data['title'] = title_element.text.strip()
            except Exception as e:
                product_data['title'] = "No title found"
                print(f"{product_data} , {e}")
            
            # Get description
            try:
                desc_element = self.driver.find_element(By.CSS_SELECTOR, ".description, .product-description, p")
                product_data['description'] = desc_element.text.strip()
            except Exception as e:
                product_data['description'] = "No description found"
                print(f"{product_data} , {e}")


            
            # Get price
            try:
                price_element = self.driver.find_element(By.CSS_SELECTOR, ".price, .product-price, [class*='price']")
                product_data['price'] = price_element.text.strip()
            except Exception as e :
                product_data['price'] = "Price not found"
                print(f"{product_data}, {e}")
                
            # Get images
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, "img")
            for img in image_elements:
                src = img.get_attribute('src')
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    full_img_url = urljoin(self.base_url, src)
                    if full_img_url not in product_data['images']:
                        product_data['images'].append(full_img_url)
            
            print(f"Found {len(product_data['images'])} images for: {product_data['title']}")
            return product_data
            
        except Exception as e:
            print(f"Error scraping product {product_url}: {e}")
            return None
    
    def download_image(self, img_url, filename):
        """Download an image from URL"""
        try:
            response = requests.get(img_url, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"Downloaded: {filename}")
            return True
            
        except Exception as e:
            print(f"Error downloading {img_url}: {e}")
            return False
    
    def save_images(self, product_data, product_index):
        """Save all images for a product"""
        if not product_data['images']:
            return
        
        # Create directory for this product
        safe_title = "".join(c for c in product_data['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        product_dir = f"images/product_{product_index}_{safe_title[:50]}"
        os.makedirs(product_dir, exist_ok=True)
        
        for i, img_url in enumerate(product_data['images']):
            # Get file extension
            parsed_url = urlparse(img_url)
            ext = os.path.splitext(parsed_url.path)[1] or '.jpg'
            
            filename = os.path.join(product_dir, f"image_{i+1}{ext}")
            self.download_image(img_url, filename)
    
    def run_scraper(self):
        """Main scraper function"""
        print("Starting Moroccan Ceramic Scraper...")
        
        # Create images directory
        os.makedirs("images", exist_ok=True)
        
        try:
            # Get product URLs
            product_urls = self.scrape_product_list()
            
            if not product_urls:
                print("No product URLs found. The website structure might have changed.")
                return
            
            # Scrape each product
            for i, url in enumerate(product_urls, 1):
                print(f"\nProcessing product {i}/{len(product_urls)}")
                
                product_data = self.scrape_product_details(url)
                if product_data:
                    self.products.append(product_data)
                    self.save_images(product_data, i)
                
                # Be respectful - add delay between requests
                time.sleep(2)
            
            # Save all product data to JSON
            with open('moroccan_ceramics.json', 'w', encoding='utf-8') as f:
                json.dump(self.products, f, indent=2, ensure_ascii=False)
            
            print(f"\nScraping completed! Found {len(self.products)} products.")
            print("Data saved to 'moroccan_ceramics.json'")
            print("Images saved to 'images/' directory")
            
        except Exception as e:
            print(f"Error during scraping: {e}")
        
        finally:
            self.driver.quit()

if __name__ == "__main__":
    scraper = MoroccanCeramicScraper()
    scraper.run_scraper()