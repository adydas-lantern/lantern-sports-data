# NAIA Wrestling Standings Scraper

Python application for scraping NAIA wrestling conference standings from 2020-2025.

## 🎯 Current Status (Last Updated: 2025-12-30)

### ✅ Complete Data Coverage (2020-2025)

**Overall Statistics:**
- **Total Schools**: 152
- **Total Data Points**: 376
- **Years Covered**: 6 (2020-2025)

**Data by Year:**
- **2025**: 60 schools (Conference Poll #2)
- **2024**: 69 schools (Conference Poll #6 - Final)
- **2023**: 65 schools (Conference Poll #7 - Final)
- **2022**: 67 schools (Conference Polls 1, 2, 6)
- **2021**: 64 schools (Conference Tournament Results)
- **2020**: 51 schools (Conference Tournament Results)

**Recent Updates:**
- ✅ Conference names normalized across all years
- ✅ Added missing schools from 2020-2021 tournament results
- ✅ Filled gaps in 2022 data (Menlo, Vanguard)
- ✅ Created sorted CSV: `NAIA_Complete_Sorted.csv`

**Historical Coverage:**
- **24 schools** with complete 6-year data
- **47 schools** with 5+ years of data
- **61 schools** with 4+ years of data

---

## 📋 How to Get NAIA Wrestling Data

### Understanding NAIA Data Sources

NAIA publishes wrestling conference standings in two formats:

1. **Conference Polls** (during season)
   - Released periodically throughout the season
   - Poll #1 = Preseason rankings
   - Higher poll numbers = later in season (more accurate)
   - Final poll (highest number) is most reliable

2. **Conference Tournament Results** (end of season)
   - Published after conference championship tournaments
   - Most accurate final standings
   - Includes all participating schools with exact placements

### Finding URLs for Each Season

NAIA wrestling standings URLs follow these patterns:

**Conference Polls:**
```
https://www.naia.org/sports/mwrest/YYYY-YY/Releases/[Poll_Name]

Examples:
- 2025-26: /Releases/Conf_2
- 2024-25: /Releases/6_Conference
- 2023-24: /Releases/7_Conference
- 2022-23: /Releases/Conference_Poll_6
- 2021-22: /Releases/Conference_Poll_7
```

**Tournament Results:**
```
https://www.naia.org/sports/mwrest/YYYY-YY/Releases/Conference-Tournaments
or
https://www.naia.org/sports/mwrest/YYYY-YY/Releases/[Year]-ConferenceTournament

Examples:
- 2021-22: /Releases/Conference-Tournaments
- 2020-21: /Releases/2021-ConferenceTournament
```

### Step-by-Step: Finding URLs for a New Season

1. **Navigate to NAIA Wrestling Site**
   - Go to: https://www.naia.org/sports/mwrest
   - Or: https://www.naia.org/sports/wrestling/men

2. **Select Season**
   - Look for season dropdown (e.g., "2025-26")
   - Navigate to that season's page

3. **Find Releases/News Section**
   - Look for "Releases", "News", or "Polls" section
   - Browse release titles for:
     - "Conference Poll" or "Conference Ratings"
     - "Conference Tournament" results
     - Any release with conference standings

4. **Test URL Format**
   - Click on a conference poll release
   - Copy the URL
   - Look for pattern: `.../Releases/[PollName]`

5. **Verify Data Structure**
   - Page should have conference names as headers
   - Followed by team rankings (1-10)
   - Data format: either "1. School - Score" or "1 School Score"

### URLs Used in This Project

See `all_scraped_urls.txt` for complete list organized by season.

**Quick Reference:**
```
2025-26: Conf_2
2024-25: 6_Conference
2023-24: 7_Conference
2022-23: Conference_Poll_1, Poll_2, Poll_6
2021-22: Conference-Tournaments (tournament results)
2020-21: 2021-ConferenceTournament (tournament results)
```

---

## Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone/Navigate to Project**
```bash
cd wrestlingStandingScreenScrape
```

2. **Create Virtual Environment**
```bash
python3 -m venv venv
```

3. **Activate Virtual Environment**
```bash
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows
```

4. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### Environment Configuration

Create/update `.env` file:
```bash
NAIA_START_URL=https://www.naia.org/sports/mwrest/2025-26/Releases/Conf_2
```

---

## Usage

### Scraping New Data

1. **Activate Environment**
```bash
source venv/bin/activate
```

2. **Update URL in .env**
```bash
NAIA_START_URL=https://www.naia.org/sports/mwrest/2024-25/Releases/6_Conference
```

3. **Run Scraper**
```bash
python main.py
```

4. **Enter Year When Prompted**
```
Which year are you scraping? (2020-2025)
Year: 2024
```

### Scraper Behavior

The scraper will:
- Parse all conference sections on the page
- Extract school names and rankings
- Match schools with existing CSV entries (partial name matching)
- Add new schools if not found (with " - Mens" suffix)
- Update the appropriate year column
- Save URL to `processed_urls.json` to prevent duplicates

### Viewing Processed URLs

Check which URLs have been scraped:
```bash
cat processed_urls.json
```

Or in Python:
```python
import json
with open('processed_urls.json') as f:
    data = json.load(f)
    for url in data['urls']:
        print(url)
```

---

## CSV Structure

`NAIA_blank - NAIA_results.csv`:

| Column | Field | Example |
|--------|-------|---------|
| A | College Division | NAIA |
| B | School | Central Baptist College - Mens |
| C | Region/Conference | American Midwest Conference/Sooner Athletic Conference |
| D | 2020 Conference Team Place | 1 |
| E | 2021 Conference Team Place | 2 |
| F | 2022 Conference Team Place | 1 |
| G | 2023 Conference Team Place | 3 |
| H | 2024 Conference Team Place | 2 |
| I | 2025 Conference Team Place | 4 |

**Normalized Conference Names:**
- `American Midwest Conference/Sooner Athletic Conference` (standardized order, no spaces around /)
- `Wolverine-Hoosier Athletic Conference` (hyphenated)
- `Kansas Collegiate Athletic Conference` (full name)
- All conference names normalized for consistency across years

`NAIA_Complete_Sorted.csv`:

| Column | Field | Example |
|--------|-------|---------|
| A | Year | 2020 |
| B | Conference | American Midwest Conference/Sooner Athletic Conference |
| C | Place | 1 |
| D | School | Williams Baptist (Ark.) - Mens |

---

## Modules

### Core Modules

**`web_parser.py`**
- HTTP requests and HTML parsing
- BeautifulSoup utilities
- Error handling for failed requests

**`csv_handler.py`**
- Read/write CSV operations
- Support for both list and dictionary formats
- UTF-8 encoding handling

**`naia_scraper.py`**
- NAIA-specific scraping logic
- Dual format parsing (numbered vs dash-separated)
- URL tracking and deduplication
- Conference and school name extraction
- Tournament format parser

**`url_finder.py`**
- URL discovery for different years
- Site structure exploration
- Pattern-based URL generation

**`main.py`**
- Application entry point
- User prompts and workflow
- CSV integration

---

## How It Works

### Parsing Formats

NAIA uses two main data formats:

**1. Numbered Format (2025-26)**
```
1 Southeastern 2162 Life University 1983 Reinhardt University 165...
```
Parsed as:
- Rank 1: Southeastern (216)
- Rank 2: Life University (198)
- Rank 3: Reinhardt University (165)

**2. Dash-Separated Format (2024-25, tournaments)**
```
1. Southeastern - 216
2. Life University - 198
3. Reinhardt University - 165
```

**3. Tournament Format (2020-21, 2021-22)**
```
1. Grand View (Iowa) - 216.5
2. Missouri Valley - 146.5
3. Graceland (Iowa) - 121.5
```

The scraper auto-detects format and parses accordingly.

### Conference Detection

1. Finds all `<strong>` tags containing "Conference"
2. Handles split conference names (e.g., "Cas" + "cade Conference")
3. Extracts next paragraph `<p>` for standings text
4. Removes "Individual Rankings" suffixes
5. Parses all schools and rankings

### School Matching Algorithm

1. **Case-insensitive partial match**: "Life University" matches "Life (Ga.) - Mens"
2. **Bidirectional matching**: Checks if A contains B OR B contains A
3. **Auto-add if no match**: Creates new row with " - Mens" suffix
4. **Updates existing**: Overwrites ranking if school found

### Data Completeness

**Schools Added from Tournament Results (2020-2021):**
- **Appalachian Athletic**: Bluefield (Va.), St. Andrews (N.C.)
- **American Midwest/Sooner**: Lincoln (Ill.), Lyon (Ark.), Hannibal-LaGrange (Mo.), Calumet (Ind.)
- **Cascade Collegiate**: Menlo (Calif.), Vanguard (Calif.), Life Pacific (Calif.), Warner Pacific (Ore.)
- **Kansas Collegiate**: Bethany (Kan.), Oklahoma Wesleyan (Okla.), Central Christian College (Kan.)
- **Mid-South**: Thomas More (Ky.), and complete standings for all schools

**Conference Name Normalization:**
All conference names have been standardized to ensure consistent data aggregation:
- Removed spacing variations around slashes
- Standardized order for dual-named conferences
- Ensures proper sorting and grouping in `NAIA_Complete_Sorted.csv`

---

## Files

### Code Files
- `web_parser.py` - Web scraping utilities (197 lines)
- `csv_handler.py` - CSV operations (199 lines)
- `naia_scraper.py` - NAIA scraper (258+ lines)
- `url_finder.py` - URL discovery (208 lines)
- `main.py` - Entry point (170 lines)

### Data Files
- `NAIA_blank - NAIA_results.csv` - Main data (152 schools, 376 data points)
- `NAIA_Complete_Sorted.csv` - Sorted by Year/Conference/Place (376 entries)
- `processed_urls.json` - Tracks 17 scraped URLs
- `.env` - Current URL configuration
- `requirements.txt` - Python dependencies

### Documentation
- `README.md` - This file
- `all_scraped_urls.txt` - Complete URL reference
- `found_urls.txt` - URLs from initial web search
- `SESSION_NOTES.md` - Session continuation notes

---

## Conference Champions (2020-2025)

### Consistent Champions (5-6 years)
- **Grand View (Iowa)** - Heart of America (2020, 2021, 2022, 2023, 2024, 2025)
- **Indiana Tech** - Wolverine Hoosier (2020, 2021, 2022, 2023, 2024, 2025)
- **Doane (Neb.)** - Great Plains (2021, 2022, 2023, 2024, 2025)

### Multiple Championships
- **Life (Ga.)** - Appalachian (2022, 2023, 2024)
- **Reinhardt (Ga.)** - Appalachian (2020, 2021)
- **Campbellsville (Ky.)** - Mid-South (2022, 2023, 2024)
- **Oklahoma City** - Sooner/American Midwest (2020, 2021, 2022, 2023, 2024, 2025)

---

## Troubleshooting

### URL Already Processed

If you see "URL already processed" but need to re-scrape:

```bash
# Remove from processed list
python -c "
import json
with open('processed_urls.json', 'r') as f:
    data = json.load(f)
data['urls'] = [u for u in data['urls'] if 'URL_TO_REMOVE' not in u]
with open('processed_urls.json', 'w') as f:
    json.dump(data, f, indent=2)
"
```

### No Data Found

If scraper finds 0 schools:
1. **Check URL is correct** - Visit in browser first
2. **Verify page format** - Inspect HTML for `<strong>Conference</strong>` tags
3. **Try different poll number** - Some polls may have different formats
4. **Check for tournament results** - May need manual entry

### School Name Mismatches

If schools don't match CSV:
1. Check `Updated [School] - [Year]: [Place]` messages in output
2. Look for new rows added at bottom of CSV
3. Manually merge duplicates if needed (e.g., "Life University" vs "Life (Ga.)")

### Parser Issues

For tournament formats that don't parse:
- See 2020 and 2021 manual entry code in `all_scraped_urls.txt`
- Tournament data may need to be manually entered

### Missing Rankings or Gaps

If you notice gaps in conference rankings (e.g., places 1, 2, 4, 5 but no 3):
1. **Check for ties** - Multiple schools may share the same ranking
2. **Verify source data** - Some schools may not have competed that year
3. **Review sorted CSV** - Use `NAIA_Complete_Sorted.csv` to verify all data
4. **Conference name variations** - Ensure conference names are normalized

---

## Development Notes

### Adding New Years

When a new season starts:

1. Find the URL using steps in "How to Get NAIA Wrestling Data"
2. Add URL to `.env`
3. Add new column to CSV header (e.g., "2026 Conference Team Place")
4. Update `main.py` year validation
5. Run scraper

### Improving Matching

To improve school name matching:
- Edit `naia_scraper.py` line ~308
- Add fuzzy matching library (e.g., `fuzzywuzzy`)
- Implement Levenshtein distance threshold

### Adding Individual Rankings

The scraper currently ignores "Individual Rankings - PDF" links.
To extract individual wrestler data:
1. Parse PDF links from page
2. Download and extract PDF data
3. Add columns for top wrestlers per school

---

## Quick Commands

**Status Check:**
```bash
python -c "
import csv
with open('NAIA_blank - NAIA_results.csv') as f:
    rows = list(csv.DictReader(f))
    years = ['2020','2021','2022','2023','2024','2025']
    for y in years:
        count = sum(1 for r in rows if r.get(f'{y} Conference Team Place','').strip())
        print(f'{y}: {count} schools')
"
```

**List Processed URLs:**
```bash
python -c "import json; print('\n'.join(json.load(open('processed_urls.json'))['urls']))"
```

**Count Total Data Points:**
```bash
python -c "
import csv
with open('NAIA_blank - NAIA_results.csv') as f:
    rows = list(csv.DictReader(f))
    total = sum(sum(1 for y in ['2020','2021','2022','2023','2024','2025']
                if r.get(f'{y} Conference Team Place','').strip()) for r in rows)
    print(f'Total data points: {total}')
"
```

**View Sorted CSV Stats:**
```bash
python -c "
import csv
from collections import Counter
with open('NAIA_Complete_Sorted.csv') as f:
    rows = list(csv.DictReader(f))
    years = Counter(r['Year'] for r in rows)
    print(f'Total entries: {len(rows)}')
    print('\nBy year:')
    for year in sorted(years.keys()):
        print(f'  {year}: {years[year]} schools')
"
```

---

## License

This project is for educational and research purposes. NAIA data belongs to the National Association of Intercollegiate Athletics.
