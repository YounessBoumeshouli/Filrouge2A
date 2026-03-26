import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin, urlparse
import time


class SimpleCeramicScraper:
    def __init__(self):
        self.base_url = "https://www.marrakeche.com"
        self.ceramic_url = "https://www.marrakeche.com/moroccan-ceramic"
        self.products = []
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def get_page(self, url):
        """Get page content with error handling"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def scrape_product_list(self):
        """Scrape the main ceramic page to get product links"""
        print("Scraping product list...")

        html = self.get_page(self.ceramic_url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")

        # Find product links - common selectors for product pages
        product_links = []

        # Try different common selectors
        selectors = [
            'a[href*="ceramic"]',
            ".product-item a",
            ".product-link",
            ".grid-item a",
            'a[href*="product"]',
            ".product a",
        ]

        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get("href")
                if href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in product_links and "ceramic" in full_url.lower():
                        product_links.append(full_url)

        print(f"Found {len(product_links)} product URLs")
        return product_links

    def scrape_product_details(self, product_url):
        """Scrape individual product page for details and images"""
        print(f"Scraping product: {product_url}")

        html = self.get_page(product_url)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        product_data = {
            "url": product_url,
            "title": "",
            "description": "",
            "price": "",
            "images": [],
        }

        # Get title
        title_selectors = ["h1", ".product-title", ".title", "h2"]
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                product_data["title"] = title_elem.get_text().strip()
                break

        # Get description
        desc_selectors = [".description", ".product-description", ".content p", "p"]
        for selector in desc_selectors:
            desc_elem = soup.select_one(selector)
            if desc_elem and len(desc_elem.get_text().strip()) > 20:
                product_data["description"] = desc_elem.get_text().strip()
                break

        # Get price
        price_selectors = [".price", ".product-price", '[class*="price"]', ".cost"]
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                product_data["price"] = price_elem.get_text().strip()
                break

        # Get images
        images = soup.find_all("img")
        for img in images:
            src = img.get("src") or img.get("data-src")
            if src and any(
                ext in src.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]
            ):
                full_img_url = urljoin(self.base_url, src)
                if full_img_url not in product_data["images"]:
                    product_data["images"].append(full_img_url)

        print(
            f"Found {len(product_data['images'])} images for: {product_data['title']}"
        )
        return product_data

    def download_image(self, img_url, filename):
        """Download an image from URL"""
        try:
            response = self.session.get(img_url, stream=True, timeout=10)
            response.raise_for_status()

            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Downloaded: {filename}")
            return True

        except Exception as e:
            print(f"Error downloading {img_url}: {e}")
            return False

    def save_images(self, product_data, product_index):
        """Save all images for a product"""
        if not product_data["images"]:
            return

        # Create directory for this product
        safe_title = "".join(
            c for c in product_data["title"] if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        product_dir = f"images/product_{product_index}_{safe_title[:50]}"
        os.makedirs(product_dir, exist_ok=True)

        for i, img_url in enumerate(product_data["images"]):
            # Get file extension
            parsed_url = urlparse(img_url)
            ext = os.path.splitext(parsed_url.path)[1] or ".jpg"

            filename = os.path.join(product_dir, f"image_{i+1}{ext}")
            self.download_image(img_url, filename)

    def run_scraper(self):
        """Main scraper function"""
        print("Starting Simple Moroccan Ceramic Scraper...")

        # Create images directory
        os.makedirs("images", exist_ok=True)

        try:
            # Get product URLs
            product_urls = self.scrape_product_list()

            if not product_urls:
                print(
                    "No product URLs found. Trying to scrape the main page for any ceramic-related content..."
                )
                # Fallback: scrape main page
                product_urls = [self.ceramic_url]

            # Scrape each product
            for i, url in enumerate(product_urls, 1):
                print(f"\nProcessing product {i}/{len(product_urls)}")

                product_data = self.scrape_product_details(url)
                if product_data:
                    self.products.append(product_data)
                    self.save_images(product_data, i)

                # Be respectful - add delay between requests
                time.sleep(1)

            # Save all product data to JSON
            with open("moroccan_ceramics_simple.json", "w", encoding="utf-8") as f:
                json.dump(self.products, f, indent=2, ensure_ascii=False)

            print(f"\nScraping completed! Found {len(self.products)} products.")
            print("Data saved to 'moroccan_ceramics_simple.json'")
            print("Images saved to 'images/' directory")

        except Exception as e:
            print(f"Error during scraping: {e}")


if __name__ == "__main__":
    scraper = SimpleCeramicScraper()
    scraper.run_scraper()
