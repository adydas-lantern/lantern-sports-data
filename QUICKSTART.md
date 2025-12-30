# Quick Start Guide

## NAIA Wrestling Scraper - Ready to Use!

Your scraper is set up and ready to go! Here's what to do:

### 1. The URL is Already Set ✓

The `.env` file already contains:
```
NAIA_START_URL=https://www.naia.org/sports/mwrest/2025-26/Releases/Conf_1
```

### 2. Run the Scraper

```bash
# Activate virtual environment
source venv/bin/activate

# Run the scraper
python main.py
```

**Note:** You need to uncomment `scrape_naia_wrestling()` in `main.py` first (line 161)

### 3. Enter the Year

When prompted:
```
Which year are you scraping? (2020-2025)
Year: 2025
```

### 4. What Happens Next

The scraper will:
- ✓ Scrape all 7-8 conferences from the page
- ✓ Extract ~58 schools with their conference rankings
- ✓ Update your CSV file automatically
- ✓ Save the URL to avoid re-scraping

### 5. Expected Output

```
Found 8 conference sections
  Appalachian Athletic Conference: 10 schools
  Cascade Collegiate Conference: 9 schools
  Great Plains Athletic Conference: 9 schools
  Heart of America Athletic Conference: 10 schools
  Kansas Collegiate Athletic Conference: 7 schools
  Sooner Athletic Conference / American Midwest Conference: 6 schools
  Wolverine Hoosier Athletic Conference: 7 schools

Successfully scraped 58 schools
CSV updated with 2025 standings
```

### 6. For Additional Years/Conferences

1. Update the URL in `.env`:
   ```
   NAIA_START_URL=https://www.naia.org/sports/mwrest/2024-25/Releases/Conf_1
   ```

2. Run again with the appropriate year

---

## Features

✓ **URL Tracking** - Never scrape the same URL twice
✓ **Multi-Conference** - Scrapes all conferences on a page
✓ **Auto-Update CSV** - Matches schools and updates rankings
✓ **Smart Parsing** - Handles NAIA's unique text format

## Files Created

- `venv/` - Python virtual environment (dependencies installed)
- `.env` - Configuration file with your URL
- `processed_urls.json` - Tracks scraped URLs (created on first run)
- All Python modules are ready to use

## Need Help?

Check `README.md` for detailed documentation or examine the example code in `main.py`.
