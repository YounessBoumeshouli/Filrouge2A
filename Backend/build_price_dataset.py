"""
Marrakech Souk — Price Reference Dataset Builder
==================================================
Sources:
  - Images : marrakech_dataset/price_tags/ (scraped images)
  - Prices : Morocco Travel Planner — Marrakech Souk Price Guide 2025/2026
              https://moroccotravelplanner.com/marrakech-souk-price-guide-and-opening-hours-2025-2026-edition/

This script:
  1. Loads the authoritative price reference table (MAD) from the guide
  2. Reads all images from the price_tags folder
  3. Matches each image to the best product category via filename/EXIF keywords
  4. Outputs a structured CSV dataset + a JSON label file ready for CV annotation
  5. Generates a quick HTML price reference card you can print/keep open while annotating

Requirements:
    pip install pandas pillow tqdm

Usage:
    python build_price_dataset.py
"""

import csv
import json
import hashlib
from pathlib import Path
from datetime import datetime
from PIL import Image
from tqdm import tqdm

# ══════════════════════════════════════════════════════════════════════════════
#  AUTHORITATIVE PRICE REFERENCE (from Morocco Travel Planner 2025/2026)
#  Source: https://moroccotravelplanner.com/marrakech-souk-price-guide...
#
#  Structure per product:
#    - category       : folder name used in the scraped dataset
#    - product        : English product name
#    - arabic_name    : local name (for OCR training, labels in Arabic numerals)
#    - souk           : where to find it
#    - price_min_mad  : minimum fair price in Moroccan Dirhams (MAD)
#    - price_max_mad  : maximum fair price in MAD
#    - notes          : extra context
# ══════════════════════════════════════════════════════════════════════════════

PRICE_REFERENCE = [
    {
        "category": "leather",
        "product": "Leather Slippers (Babouches)",
        "arabic_name": "بلغة",
        "souk": "Souk Smata / Souk Cherratine",
        "price_min_mad": 80,
        "price_max_mad": 150,
        "notes": "Traditional pointed-toe leather slippers. Price rises with embroidery quality.",
    },
    {
        "category": "leather",
        "product": "Leather Bag",
        "arabic_name": "شنطة جلدية",
        "souk": "Souk Cherratine",
        "price_min_mad": 200,
        "price_max_mad": 600,
        "notes": "Handmade backpacks, purses, belts. Quality varies widely.",
    },
    {
        "category": "crafts",
        "product": "Small Tagine Pot",
        "arabic_name": "طاجين",
        "souk": "Souk Semmarine",
        "price_min_mad": 20,
        "price_max_mad": 50,
        "notes": "Decorative or functional clay cooking pot.",
    },
    {
        "category": "crafts",
        "product": "Ceramic Bowl",
        "arabic_name": "طبق خزفي",
        "souk": "Souk Semmarine / Chabi Chic",
        "price_min_mad": 50,
        "price_max_mad": 150,
        "notes": "Hand-painted. Larger decorative pieces cost more.",
    },
    {
        "category": "crafts",
        "product": "Handwoven Basket",
        "arabic_name": "سلة مصنوعة يدويا",
        "souk": "Souk Chouari / Rahba Kedima",
        "price_min_mad": 100,
        "price_max_mad": 200,
        "notes": "Colorful, lightweight. Good travel souvenir.",
    },
    {
        "category": "textiles",
        "product": "Scarf",
        "arabic_name": "وشاح",
        "souk": "Souk Semmarine / Souk Ahiak",
        "price_min_mad": 50,
        "price_max_mad": 70,
        "notes": "Lightweight cotton or silk blend.",
    },
    {
        "category": "textiles",
        "product": "Small Silk Rug",
        "arabic_name": "زربية صغيرة",
        "souk": "Souk Zrabi",
        "price_min_mad": 300,
        "price_max_mad": 800,
        "notes": "Handwoven. Price depends heavily on size and knot density.",
    },
    {
        "category": "textiles",
        "product": "Berber Carpet / Beni Ourain Rug",
        "arabic_name": "زربية بربرية",
        "souk": "Souk Zrabi / 33 Rue Majorelle",
        "price_min_mad": 800,
        "price_max_mad": 5000,
        "notes": "High-end handcrafted rugs. Shipping often available from shops.",
    },
    {
        "category": "textiles",
        "product": "Kaftan / Djellaba",
        "arabic_name": "قفطان / جلابة",
        "souk": "Souk Ahiak / boutiques in Gueliz",
        "price_min_mad": 150,
        "price_max_mad": 1500,
        "notes": "Price varies hugely by fabric quality and embroidery detail.",
    },
    {
        "category": "lanterns",
        "product": "Brass Lantern (small–medium)",
        "arabic_name": "فانوس نحاسي",
        "souk": "Souk Haddadine",
        "price_min_mad": 100,
        "price_max_mad": 500,
        "notes": "From guide table. More elaborate/large ones: 300–800 MAD.",
    },
    {
        "category": "lanterns",
        "product": "Moroccan Lantern (large / decorative)",
        "arabic_name": "فانوس مغربي كبير",
        "souk": "Souk Haddadine / Chabi Chic",
        "price_min_mad": 300,
        "price_max_mad": 800,
        "notes": "Metal and glass. Creates stunning shadow patterns when lit.",
    },
    {
        "category": "argan",
        "product": "Argan Oil (medium bottle)",
        "arabic_name": "زيت أركان",
        "souk": "Souk El Attarine / Arganino / Assouss Argane",
        "price_min_mad": 150,
        "price_max_mad": 300,
        "notes": "Morocco's 'liquid gold'. Real argan oil: thick paste, strong nut smell.",
    },
    {
        "category": "spices",
        "product": "Spices (per 100g)",
        "arabic_name": "بهارات",
        "souk": "Rahba Kedima / Souk Ableuh / Souk El Attarine",
        "price_min_mad": 30,
        "price_max_mad": 80,
        "notes": "Cumin, saffron, ras el hanout, dried rosebuds. Price by weight.",
    },
    {
        "category": "jewelry",
        "product": "Brass / Silver Jewelry",
        "arabic_name": "مجوهرات",
        "souk": "Souk des Bijoutiers",
        "price_min_mad": 100,
        "price_max_mad": 3000,
        "notes": "Berber cuffs, earrings, Tuareg designs. Vintage pieces cost more.",
    },
    {
        "category": "price_tags",
        "product": "Perfume / Solid Musk",
        "arabic_name": "عطر / مسك",
        "souk": "Souk El Attarine / Maison De La Parfum Marrakech",
        "price_min_mad": 50,
        "price_max_mad": 300,
        "notes": "Sold as stones or essential oils.",
    },
]

# Keyword → category mapping for auto-labelling images by filename
KEYWORD_MAP = {
    "slipper": "leather",
    "babouche": "leather",
    "bag": "leather",
    "leather": "leather",
    "cuir": "leather",
    "spice": "spices",
    "épice": "spices",
    "epice": "spices",
    "saffron": "spices",
    "cumin": "spices",
    "ras": "spices",
    "tagine": "crafts",
    "ceramic": "crafts",
    "pottery": "crafts",
    "basket": "crafts",
    "wood": "crafts",
    "scarf": "textiles",
    "carpet": "textiles",
    "rug": "textiles",
    "textile": "textiles",
    "kaftan": "textiles",
    "djellaba": "textiles",
    "lantern": "lanterns",
    "lamp": "lanterns",
    "fano": "lanterns",
    "argan": "argan",
    "oil": "argan",
    "jewelry": "jewelry",
    "jewel": "jewelry",
    "silver": "jewelry",
    "ring": "jewelry",
    "bracelet": "jewelry",
    "price": "price_tags",
    "tag": "price_tags",
    "label": "price_tags",
    "dirham": "price_tags",
    "mad": "price_tags",
}


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════


def guess_category(filename: str) -> str:
    name = filename.lower()
    for kw, cat in KEYWORD_MAP.items():
        if kw in name:
            return cat
    return "unknown"


def image_info(path: Path) -> dict:
    try:
        with Image.open(path) as img:
            w, h = img.size
            mode = img.mode
    except Exception:
        w, h, mode = 0, 0, "?"
    size_kb = round(path.stat().st_size / 1024, 1)
    h_md5 = hashlib.md5(path.read_bytes()).hexdigest()[:10]
    return {"width": w, "height": h, "mode": mode, "size_kb": size_kb, "hash": h_md5}


def price_range_str(row: dict) -> str:
    return f"{row['price_min_mad']}–{row['price_max_mad']} MAD"


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

DATASET_ROOT = Path("marrakech_dataset")
OUTPUT_CSV = Path("marrakech_price_dataset.csv")
OUTPUT_JSON = Path("marrakech_price_labels.json")
OUTPUT_HTML = Path("price_reference_card.html")


def build_csv_dataset():
    """Walk all image subfolders and build a CSV with category + price reference."""
    rows = []
    image_extensions = {".jpg", ".jpeg", ".png", ".webp"}

    # Build a quick lookup: category → price row(s)
    price_lookup: dict[str, list] = {}
    for p in PRICE_REFERENCE:
        price_lookup.setdefault(p["category"], []).append(p)

    if not DATASET_ROOT.exists():
        print(f"⚠️  Dataset folder '{DATASET_ROOT}' not found.")
        print("   Run marrakech_scraper.py first, then re-run this script.")
        return []

    all_images = [
        f
        for f in DATASET_ROOT.rglob("*")
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    print(f"📂 Found {len(all_images)} images in '{DATASET_ROOT}'")

    for img_path in tqdm(all_images, desc="Processing images"):
        rel = img_path.relative_to(DATASET_ROOT)
        parts = rel.parts
        folder_cat = parts[0] if len(parts) > 1 else "unknown"
        filename_cat = guess_category(img_path.name)
        category = folder_cat if folder_cat != "unknown" else filename_cat

        info = image_info(img_path)
        price_rows = price_lookup.get(category, [{}])
        ref = price_rows[0]  # take first match as primary reference

        rows.append(
            {
                "filepath": str(img_path),
                "filename": img_path.name,
                "folder_category": folder_cat,
                "inferred_category": filename_cat,
                "final_category": category,
                "product": ref.get("product", ""),
                "arabic_name": ref.get("arabic_name", ""),
                "souk_location": ref.get("souk", ""),
                "price_min_mad": ref.get("price_min_mad", ""),
                "price_max_mad": ref.get("price_max_mad", ""),
                "price_range": price_range_str(ref) if ref else "",
                "notes": ref.get("notes", ""),
                "width_px": info["width"],
                "height_px": info["height"],
                "size_kb": info["size_kb"],
                "hash": info["hash"],
                "annotated": "no",  # to be filled during annotation
                "annotation_file": "",
            }
        )

    # Write CSV
    if rows:
        fieldnames = list(rows[0].keys())
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Dataset CSV saved → {OUTPUT_CSV}  ({len(rows)} rows)")
    return rows


def build_json_labels():
    """Export price reference as JSON for use in annotation tools."""
    payload = {
        "meta": {
            "source": "Morocco Travel Planner — Marrakech Souk Price Guide 2025/2026",
            "url": "https://moroccotravelplanner.com/marrakech-souk-price-guide-and-opening-hours-2025-2026-edition/",
            "currency": "MAD (Moroccan Dirham)",
            "generated_at": datetime.now().isoformat(),
            "note": "Prices are averages. Haggling expected. Deeper in souks = lower prices.",
        },
        "categories": list({p["category"] for p in PRICE_REFERENCE}),
        "price_reference": PRICE_REFERENCE,
    }
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"✅ Labels JSON saved → {OUTPUT_JSON}")


def build_html_reference_card():
    """Generate a printable HTML price reference card."""
    rows_html = ""
    for p in PRICE_REFERENCE:
        badge_color = {
            "spices": "#e67e22",
            "leather": "#8B4513",
            "crafts": "#27ae60",
            "textiles": "#8e44ad",
            "lanterns": "#f39c12",
            "argan": "#16a085",
            "jewelry": "#2980b9",
            "price_tags": "#e74c3c",
        }.get(p["category"], "#7f8c8d")

        rows_html += f"""
        <tr>
          <td><span class="badge" style="background:{badge_color}">{p['category']}</span></td>
          <td><strong>{p['product']}</strong><br><small class="arabic">{p['arabic_name']}</small></td>
          <td>{p['souk']}</td>
          <td class="price">{p['price_min_mad']}–{p['price_max_mad']} MAD</td>
          <td><small>{p['notes']}</small></td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Marrakech Souk Price Reference — 2025/2026</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #fdf6ec; color: #333; padding: 20px; }}
  h1 {{ color: #c0392b; text-align: center; margin-bottom: 4px; font-size: 1.6em; }}
  .subtitle {{ text-align: center; color: #7f8c8d; font-size: .85em; margin-bottom: 18px; }}
  .source {{ text-align: center; font-size: .75em; color: #aaa; margin-bottom: 20px; }}
  table {{ width: 100%; border-collapse: collapse; background: white;
           box-shadow: 0 2px 8px rgba(0,0,0,.1); border-radius: 8px; overflow: hidden; }}
  th {{ background: #c0392b; color: white; padding: 10px 12px; text-align: left; font-size: .9em; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #f0e6d3; vertical-align: top; font-size: .88em; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #fef9f3; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px;
            color: white; font-size: .75em; font-weight: bold; text-transform: uppercase; }}
  .price {{ font-weight: bold; color: #c0392b; white-space: nowrap; }}
  .arabic {{ direction: rtl; display: block; color: #888; font-size: .85em; }}
  .tip-box {{ background: #ffeaa7; border-left: 4px solid #f39c12; padding: 12px 16px;
              margin-top: 20px; border-radius: 4px; font-size: .9em; }}
  .tip-box strong {{ color: #d68910; }}
  @media print {{ body {{ background: white; }} .tip-box {{ break-inside: avoid; }} }}
</style>
</head>
<body>

<h1>🏺 Marrakech Souk Price Reference</h1>
<p class="subtitle">2025 / 2026 Edition — All prices in Moroccan Dirhams (MAD)</p>
<p class="source">Source: Morocco Travel Planner — moroccotravelplanner.com &nbsp;|&nbsp; Generated: {datetime.now().strftime('%Y-%m-%d')}</p>

<table>
  <thead>
    <tr>
      <th>Category</th>
      <th>Product</th>
      <th>Souk / Location</th>
      <th>Price Range (MAD)</th>
      <th>Notes</th>
    </tr>
  </thead>
  <tbody>
    {rows_html}
  </tbody>
</table>

<div class="tip-box">
  <strong>💡 Haggling Tips:</strong>
  Start at ~⅓ of the asking price · Stay friendly & polite ·
  Bundle purchases for better deals · Walk away if needed — the best price often follows.
  <br><br>
  <strong>⏰ Opening hours:</strong> Most shops open 10:00 AM – 7:30 PM (some near Jemaa el-Fna until 11:30 PM).
  Fridays are slower. During Ramadan hours may shift.
  <br><br>
  <strong>💱 Quick conversion:</strong> 1 EUR ≈ 11 MAD &nbsp;|&nbsp; 1 USD ≈ 10 MAD &nbsp;(check current rate)
</div>

</body>
</html>"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Price reference card saved → {OUTPUT_HTML}")


# ══════════════════════════════════════════════════════════════════════════════
#  RUN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  Marrakech Souk — Price Reference Dataset Builder")
    print("=" * 60)

    build_json_labels()
    build_html_reference_card()
    rows = build_csv_dataset()

    print("\n" + "=" * 60)
    print("  📦 OUTPUT FILES")
    print(f"  {OUTPUT_CSV}         ← main dataset (images + prices)")
    print(f"  {OUTPUT_JSON}   ← price labels for annotation tools")
    print(f"  {OUTPUT_HTML}     ← printable price reference card")
    print("=" * 60)
    print("\n  NEXT STEPS:")
    print(
        "  1. Open price_reference_card.html in browser (great reference while annotating)"
    )
    print(
        "  2. Upload marrakech_price_dataset.csv + images to Roboflow or Label Studio"
    )
    print("  3. Draw bounding boxes around price tags in the price_tags/ images")
    print("  4. Use marrakech_price_labels.json to assign correct price categories")
    print("  5. Train EasyOCR / PaddleOCR on the annotated dataset")
    print("=" * 60)
