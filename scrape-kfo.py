#!/usr/bin/env python3
"""
KFO Merino Yarn Scraper - Download images and extract hex colors
"""

import requests
from bs4 import BeautifulSoup
from PIL import Image
import os
import json
import time
from urllib.parse import urljoin

# ===== CONFIGURATION =====
BASE_URL = "https://knittingforolive.com"
# This is the typical URL pattern - adjust after testing
COLLECTION_URL = f"{BASE_URL}/collections/knitting-for-olives-merino"

OUTPUT_DIR = "./kfo_yarn_data"
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Be polite to the server
DELAY_BETWEEN_REQUESTS = 1  # seconds


def scrape_yarn_collection():
    """
    Scrape the KFO Merino collection page for yarn links
    """
    print(f"Scraping collection page: {COLLECTION_URL}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    response = requests.get(COLLECTION_URL, headers=headers)
    
    if response.status_code != 200:
        print(f"Error: Could not access {COLLECTION_URL}")
        print(f"Status code: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all product links (adjust selectors based on actual HTML)
    # Common patterns: .product-card, .product-item, a[href*='/products/']
    product_links = []
    
    # Try multiple common selectors
    selectors = [
        'a[href*="/products/merino"]',
        '.product-card a',
        '.product-item a',
        'a.product-link'
    ]
    
    for selector in selectors:
        links = soup.select(selector)
        if links:
            print(f"Found {len(links)} products using selector: {selector}")
            for link in links:
                href = link.get('href')
                if href and '/products/' in href:
                    full_url = urljoin(BASE_URL, href)
                    if full_url not in product_links:
                        product_links.append(full_url)
            break
    
    print(f"Total unique product links found: {len(product_links)}")
    return product_links


def scrape_yarn_details(product_url):
    """
    Scrape individual yarn product page for details and image
    """
    print(f"Scraping: {product_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    response = requests.get(product_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error accessing {product_url}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract yarn details (adjust selectors based on actual HTML)
    yarn_data = {
        'url': product_url,
        'name': None,
        'color': None,
        'image_url': None,
        'price': None
    }
    
    # Try to find product title
    title_selectors = ['h1.product-title', 'h1', '.product-title', 'title']
    for selector in title_selectors:
        title = soup.select_one(selector)
        if title:
            yarn_data['name'] = title.get_text().strip()
            break
    
    # Try to find main product image
    image_selectors = [
        'img.product-image',
        '.product-gallery img',
        'img[src*="merino"]',
        '.main-image img'
    ]
    for selector in image_selectors:
        img = soup.select_one(selector)
        if img:
            image_url = img.get('src') or img.get('data-src')
            if image_url:
                yarn_data['image_url'] = urljoin(BASE_URL, image_url)
                break
    
    # Try to find price
    price_selectors = ['.price', '.product-price', 'span[class*="price"]']
    for selector in price_selectors:
        price = soup.select_one(selector)
        if price:
            yarn_data['price'] = price.get_text().strip()
            break
    
    return yarn_data


def download_image(image_url, yarn_name):
    """
    Download yarn image
    """
    print(f"Downloading image: {yarn_name}")
    
    try:
        response = requests.get(image_url, timeout=10)
        
        if response.status_code == 200:
            # Create safe filename
            safe_name = "".join(c for c in yarn_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"{safe_name}.jpg"
            filepath = os.path.join(IMAGES_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Saved: {filepath}")
            return filepath
        else:
            print(f"Failed to download: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None


def extract_hex_from_image(image_path):
    """
    Extract hex color from yarn image
    Uses center crop and averaging
    """
    print(f"Extracting hex from: {os.path.basename(image_path)}")
    
    try:
        img = Image.open(image_path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get center region (middle 40% of image to avoid edges/labels)
        width, height = img.size
        left = int(width * 0.3)
        top = int(height * 0.3)
        right = int(width * 0.7)
        bottom = int(height * 0.7)
        
        center_crop = img.crop((left, top, right, bottom))
        
        # Resize to 1x1 to get average color
        center_crop = center_crop.resize((1, 1), Image.Resampling.LANCZOS)
        avg_color = center_crop.getpixel((0, 0))
        
        r, g, b = avg_color
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        
        print(f"Extracted: {hex_color}")
        return hex_color
        
    except Exception as e:
        print(f"Error extracting hex: {e}")
        return None


def main():
    all_yarn_data = []
    
    # Step 1: Get all product links
    print("Scraping collection page...")
    product_links = scrape_yarn_collection()
    
    if not product_links:
        print("No products found. The website structure may have changed.")
        print("Please check the URL and HTML selectors in the script.")
        return
    
    # Step 2: Scrape each product
    print(f"Scraping {len(product_links)} individual products...")
    for i, url in enumerate(product_links, 1):
        print(f"Product {i}/{len(product_links)}")
        
        yarn_data = scrape_yarn_details(url)
        
        if yarn_data and yarn_data['image_url']:
            all_yarn_data.append(yarn_data)
        
        # Be polite - don't hammer the server
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Step 3: Download images
    print(f"Downloading {len(all_yarn_data)} images...")
    for yarn_data in all_yarn_data:
        if yarn_data['image_url']:
            filepath = download_image(yarn_data['image_url'], yarn_data['name'])
            yarn_data['local_image_path'] = filepath
            time.sleep(0.5)  # Brief delay between downloads
    
    # Step 4: Extract hex colors
    print(f"Extracting hex colors...")
    for yarn_data in all_yarn_data:
        if yarn_data.get('local_image_path'):
            hex_color = extract_hex_from_image(yarn_data['local_image_path'])
            yarn_data['hex_color'] = hex_color
    
    # Save results to JSON
    output_file = os.path.join(OUTPUT_DIR, "yarn_data.json")
    with open(output_file, 'w') as f:
        json.dump(all_yarn_data, f, indent=2)
    
    print("scraping complete!")
    print(f"Total yarns processed: {len(all_yarn_data)}")
    print(f"Images saved to: {IMAGES_DIR}")
    print(f"Data saved to: {output_file}")
    
    # Print summary
    print("Sample results:")
    for yarn in all_yarn_data[:5]:
        print(f"  Name: {yarn['name']}")
        print(f"  Hex: {yarn.get('hex_color', 'N/A')}")


if __name__ == "__main__":
    main()
