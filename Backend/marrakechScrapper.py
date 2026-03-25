"""
Marrakech Souk Product Image Scraper
=====================================
Scrapes images of Marrakech souk products WITH visible prices from:
  - Google Images (via icrawler)
  - Flickr (via icrawler)
  - Bing Images (via icrawler)

Saves images in organized folders by category and logs metadata to CSV.

Requirements:
    pip install icrawler requests pillow pandas tqdm

Usage:
    python marrakech_scraper.py
"""

import os
import csv
import time
import hashlib
import pandas as pd
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

# ── icrawler imports ──────────────────────────────────────────────────────────
from icrawler.builtin import GoogleImageCrawler, BingImageCrawler, FlickrImageCrawler

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

OUTPUT_DIR = Path("marrakech_dataset")   # Root folder for all downloaded images
IMAGES_PER_QUERY = 50                    # Images to download per search query
LOG_FILE = OUTPUT_DIR / "metadata.csv"   # CSV log of all downloaded images

# Search queries — each maps to a product category.
# Queries are crafted to maximise chance of images WITH price tags/labels.
SEARCH_QUERIES = {
    "spices": [
        "Marrakech souk spices price tag",
        "moroccan spice market price label",
        "Marrakech épices prix étiquette",
        "souk marrakech spices stall prices",
    ],
    "leather": [
        "Marrakech leather goods price souk",
        "moroccan leather bag price tag market",
        "Marrakech maroquinerie prix étiquette",
        "souk leather sandals price marrakech",
    ],
    "crafts": [
        "Marrakech handicrafts price tag souk",
        "moroccan crafts market price label",
        "artisanat marrakech prix étiquette",
        "marrakech pottery price souk stall",
    ],
    "textiles": [
        "Marrakech carpet rug price tag souk",
        "moroccan textile market price label",
        "tapis marrakech prix étiquette souk",
        "marrakech fabric market price sign",
    ],
    "lanterns": [
        "Marrakech lantern lamp price souk",
        "moroccan metal lantern market price",
        "souk marrakech lampe prix étiquette",
    ],
    "argan": [
        "Marrakech argan oil price tag souk",
        "moroccan argan products market price",
        "huile argan marrakech prix étiquette",
    ],
    "jewelry": [
        "Marrakech silver jewelry price souk",
        "moroccan jewelry market price tag",
        "bijoux marrakech souk prix étiquette",
    ],
    "price_tags": [
        "moroccan market price tag closeup",
        "souk marrakech price label",
        "prix étiquette souk maroc",
        "marrakech shop price sign dirham",
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def make_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def init_log(log_path: Path):
    """Create CSV log file with headers if it doesn't exist."""
    if not log_path.exists():
        with open(log_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "filename", "category", "query", "source",
                "timestamp", "file_size_kb", "hash"
            ])


def log_image(log_path: Path, row: dict):
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "filename", "category", "query", "source",
            "timestamp", "file_size_kb", "hash"
        ])
        writer.writerow(row)


def file_hash(path: Path) -> str:
    """MD5 hash of file contents — used to detect duplicates."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def remove_duplicates(folder: Path):
    """Remove duplicate images (same hash) within a folder."""
    seen = {}
    removed = 0
    for img in folder.glob("*.*"):
        if img.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        h = file_hash(img)
        if h in seen:
            img.unlink()
            removed += 1
        else:
            seen[h] = img
    return removed


# ══════════════════════════════════════════════════════════════════════════════
#  SCRAPERS
# ══════════════════════════════════════════════════════════════════════════════

def scrape_google(query: str, save_dir: Path, max_num: int):
    crawler = GoogleImageCrawler(
        feeder_threads=1,
        parser_threads=2,
        downloader_threads=4,
        storage={"root_dir": str(save_dir)},
    )
    crawler.crawl(
        keyword=query,
        max_num=max_num,
        min_size=(200, 200),        # Skip tiny thumbnails
        file_idx_offset="auto",
    )


def scrape_bing(query: str, save_dir: Path, max_num: int):
    crawler = BingImageCrawler(
        feeder_threads=1,
        parser_threads=2,
        downloader_threads=4,
        storage={"root_dir": str(save_dir)},
    )
    crawler.crawl(
        keyword=query,
        max_num=max_num,
        min_size=(200, 200),
        file_idx_offset="auto",
    )


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def run():
    print("=" * 60)
    print("  Marrakech Souk Image Scraper")
    print(f"  Output directory : {OUTPUT_DIR.resolve()}")
    print(f"  Images per query : {IMAGES_PER_QUERY}")
    print("=" * 60)

    make_dir(OUTPUT_DIR)
    init_log(LOG_FILE)

    total_downloaded = 0
    total_duplicates = 0

    for category, queries in SEARCH_QUERIES.items():
        cat_dir = OUTPUT_DIR / category
        make_dir(cat_dir)

        print(f"\n📦 Category: {category.upper()}")

        for query in queries:
            print(f"  🔍 Query: '{query}'")

            # Alternate between Google and Bing for diversity
            for source, scrape_fn in [("google", scrape_google), ("bing", scrape_bing)]:
                sub_dir = cat_dir / source
                make_dir(sub_dir)

                before = set(sub_dir.glob("*.*"))
                try:
                    scrape_fn(query, sub_dir, max_num=IMAGES_PER_QUERY // 2)
                except Exception as e:
                    print(f"    ⚠️  {source} error: {e}")
                    continue

                after = set(sub_dir.glob("*.*"))
                new_files = after - before
                count = len(new_files)
                total_downloaded += count

                # Log each new file
                for img_path in new_files:
                    try:
                        size_kb = round(img_path.stat().st_size / 1024, 2)
                        h = file_hash(img_path)
                        log_image(LOG_FILE, {
                            "filename": img_path.name,
                            "category": category,
                            "query": query,
                            "source": source,
                            "timestamp": datetime.now().isoformat(),
                            "file_size_kb": size_kb,
                            "hash": h,
                        })
                    except Exception:
                        pass

                print(f"    ✅ {source}: +{count} images")
                time.sleep(1.5)  # Be polite — avoid rate limiting

        # Deduplicate within category
        dupes = remove_duplicates(cat_dir)
        total_duplicates += dupes
        if dupes:
            print(f"  🗑️  Removed {dupes} duplicate images in '{category}'")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  ✅ SCRAPING COMPLETE")
    print(f"  Total images downloaded : {total_downloaded}")
    print(f"  Duplicates removed      : {total_duplicates}")
    print(f"  Net images kept         : {total_downloaded - total_duplicates}")
    print(f"  Metadata log            : {LOG_FILE.resolve()}")
    print("=" * 60)

    # Print per-category summary
    print("\n📊 Images per category:")
    for category in SEARCH_QUERIES:
        cat_dir = OUTPUT_DIR / category
        count = sum(1 for _ in cat_dir.rglob("*.jpg")) + \
                sum(1 for _ in cat_dir.rglob("*.jpeg")) + \
                sum(1 for _ in cat_dir.rglob("*.png"))
        print(f"  {category:<15} : {count} images")


# ══════════════════════════════════════════════════════════════════════════════
#  BONUS: Dataset summary after scraping
# ══════════════════════════════════════════════════════════════════════════════

def print_summary():
    """Load and display metadata CSV summary."""
    if not LOG_FILE.exists():
        print("No metadata log found. Run the scraper first.")
        return

    df = pd.read_csv(LOG_FILE)
    print("\n📈 Dataset Summary")
    print(df.groupby(["category", "source"]).size().unstack(fill_value=0).to_string())
    print(f"\nTotal: {len(df)} images | Avg size: {df['file_size_kb'].mean():.1f} KB")


if __name__ == "__main__":
    run()
    print_summary()