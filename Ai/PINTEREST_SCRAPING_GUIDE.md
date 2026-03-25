# Pinterest Image Scraping Solutions

## 🎯 Goal
Download Pinterest images for `product_51_Handcrafted Tamegroute Ceramic Cake Stand with Sca` starting from `image_20.jpg`

## 🛠️ Solutions Created

### 1. Browser-Based Collector (RECOMMENDED) ⭐
**File**: `pinterest_image_collector.html`

**How to use**:
1. Open `pinterest_image_collector.html` in your browser
2. Click "Search Pinterest" to open Pinterest
3. Right-click on images → "Copy image address"
4. Paste URLs in the HTML tool
5. Generate and run the Python download script

**Advantages**:
- ✅ Works with Pinterest's current interface
- ✅ User-friendly HTML interface
- ✅ Generates custom download script
- ✅ No browser automation issues

### 2. Manual Download Script
**File**: `manual_downloader.py` (created in product folder)

**How to use**:
1. Edit the script and add Pinterest image URLs
2. Run: `python manual_downloader.py`

### 3. Multi-Source Scraper
**File**: `multi_source_scraper.py`

**Features**:
- Creates manual download tools
- Provides Pinterest search links
- Handles multiple image sources

## 📁 File Locations

- **Target Folder**: `c:\Users\boume\Briefs\Filrouge2A\images\product_51_Handcrafted Tamegroute Ceramic Cake Stand with Sca`
- **Starting Number**: `image_20.jpg`
- **HTML Helper**: `pinterest_image_collector.html`
- **Scripts**: `c:\Users\boume\Briefs\Filrouge2A\Ai\`

## 🔗 Pinterest Search URL
```
https://www.pinterest.com/search/pins/?q=Handcrafted%20Tamegroute%20Ceramic%20Cake%20Stand
```

## 📋 Step-by-Step Process

### Method 1: HTML Helper (Easiest)
1. Open `pinterest_image_collector.html`
2. Click "Search Pinterest"
3. Right-click images → "Copy image address"
4. Paste URLs in the HTML form
5. Click "Process URLs"
6. Copy the generated Python code
7. Save as `download_images.py`
8. Run: `python download_images.py`

### Method 2: Manual Collection
1. Go to Pinterest search URL
2. Find ceramic cake stand images
3. Right-click → "Copy image address"
4. Edit `manual_downloader.py`
5. Add URLs to the `IMAGE_URLS` list
6. Run the script

## 💡 Tips for Best Results

### Finding High-Quality Images
- Look for URLs containing `/736x/` (high resolution)
- Avoid `/236x/` (thumbnail size)
- Right-click on the actual image, not the pin

### URL Format Examples
```
✅ Good: https://i.pinimg.com/736x/ab/cd/ef/abcdef123456.jpg
❌ Avoid: https://i.pinimg.com/236x/ab/cd/ef/abcdef123456.jpg
```

### Image Naming
- Images will be saved as: `image_20.jpg`, `image_21.jpg`, etc.
- Automatically skips existing files
- Converts all formats to JPEG
- Resizes large images to max 1024px

## 🚫 Why Selenium Failed

Pinterest uses heavy JavaScript and anti-bot measures:
- Dynamic content loading
- CAPTCHA challenges
- IP-based blocking
- Session requirements

Manual collection is more reliable and respectful to Pinterest's terms of service.

## 📊 Expected Results

After running the download script:
- **New images**: 10-15 ceramic cake stand images
- **File names**: `image_20.jpg` to `image_34.jpg` (approximately)
- **Location**: Product_51 folder
- **Format**: JPEG, optimized for YOLO training

## 🔄 Integration with YOLO Training

Once you have the new images:
1. Create corresponding label files (`.txt`) with bounding boxes
2. Re-run the dataset preparation: `python prepare_and_train.py`
3. Train the YOLO model with expanded dataset

The additional images will improve your YOLO model's accuracy for detecting ceramic cake stands!

## 🎉 Summary

The browser-based HTML collector provides the most reliable way to gather Pinterest images while respecting the platform's terms of service. The generated download scripts will automatically save images with the correct naming convention for your YOLO dataset.