# Yarn Color Combo Interface - MVP

Web scraper for Knitting for Olive Merino yarn images with hex color extraction.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the scraper:**
   ```bash
   python scrape-kfo.py
   ```

3. **Check results:**
   - Images: `./kfo_yarn_data/images/`
   - Data: `./kfo_yarn_data/yarn_data.json`

## What It Does

The scraper:
1. Scrapes the KFO Merino collection page (https://knittingforolive.com/collections/merino)
2. Finds all individual yarn product pages
3. Downloads product images
4. Extracts hex color codes from center of each image
5. Saves everything to JSON

## Output Structure

```json
[
  {
    "url": "https://knittingforolive.com/products/merino-oak",
    "name": "Merino - Oak",
    "color": "Oak",
    "image_url": "https://...",
    "local_image_path": "./kfo_yarn_data/images/Merino_Oak.jpg",
    "hex_color": "#a67c52"
  }
]
```

## Customization

If the scraper doesn't find products, you may need to adjust HTML selectors:

1. Visit https://knittingforolive.com/collections/merino
2. Inspect the HTML structure
3. Update these sections in `scrape_kfo.py`:
   - `selectors` list in `scrape_yarn_collection()` - finds product links
   - `title_selectors` in `scrape_yarn_details()` - finds product names
   - `image_selectors` in `scrape_yarn_details()` - finds product images

## Rate Limiting

The script includes:
- 1 second delay between product page requests
- 0.5 second delay between image downloads

This is respectful to KFO's servers. Don't reduce these delays.

## Hex Color Extraction

Current method:
- Crops center 40% of image (30%-70% on each axis)
- Averages all pixels in that region
- Converts to hex code

**Validation steps:**
1. Run the scraper on ~10 yarns first
2. Manually compare extracted hex codes to actual yarn colors
3. Adjust crop percentages if needed
4. Add blur/smoothing if colors are too noisy

## Next Steps

After validating the extracted colors:
1. Load `yarn_data.json` into SQL database
2. Create color combination cards dataset
3. Build frontend interface
