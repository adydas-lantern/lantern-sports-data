# Adding NCAA Wrestling Data Guide

This guide explains how to add NCAA Division I and Division II wrestling standings data to the API.

## Architecture Overview

The API is designed to support multiple sports, divisions, and genders through a flexible filtering system:

**Current Data:**
- Sport: `wrestling`
- Division: `naia`
- Gender: `mens`

**NCAA Support:**
- Sport: `wrestling`
- Division: `ncaa-d1` (NCAA Division I), `ncaa-d2` (NCAA Division II), `ncaa-d3` (NCAA Division III)
- Gender: `mens`, `womens`

## Data Sources

### NCAA Division I Wrestling

**Official Sources:**
- **NCAA Wrestling Championships**: https://www.ncaa.com/sports/wrestling/d1
- **Conference Websites**: Each conference (Big Ten, Big 12, ACC, etc.) publishes standings
- **TrackWrestling**: https://www.trackwrestling.com/ (comprehensive results)
- **FloWrestling**: https://www.flowrestling.org/ (rankings and results)

**Key Conferences (D1):**
- Big Ten Conference
- Big 12 Conference
- Atlantic Coast Conference (ACC)
- Eastern Intercollegiate Wrestling Association (EIWA)
- Mid-American Conference (MAC)
- Pacific-12 Conference (Pac-12)
- Southern Conference (SoCon)
- Eastern Wrestling League (EWL)

### NCAA Division II Wrestling

**Official Sources:**
- **NCAA D2 Wrestling**: https://www.ncaa.com/sports/wrestling/d2
- **Conference websites** for specific standings

**Key Conferences (D2):**
- Rocky Mountain Athletic Conference (RMAC)
- Northern Sun Intercollegiate Conference (NSIC)
- Great Midwest Athletic Conference (GMAC)
- Mid-America Intercollegiate Athletics Association (MIAA)
- Pennsylvania State Athletic Conference (PSAC)
- South Atlantic Conference (SAC)
- Super Region tournaments

### NCAA Division III Wrestling

**Official Sources:**
- **NCAA D3 Wrestling**: https://www.ncaa.com/sports/wrestling/d3
- Regional tournament results

**Regional Structure:**
- Northeast Region
- Mid-Atlantic Region
- Midwest Region
- Central Region
- West Region
- Southeast Region

## CSV Data Structure

### Adding NCAA Data to Main CSV

The CSV structure already supports NCAA data. Add rows with:

```csv
Sport,Division,Gender,College Division,School,Region,2020 Conference Team Place,2021 Conference Team Place,2022 Conference Team Place,2023 Conference Team Place,2024 Conference Team Place,2025 Conference Team Place
wrestling,ncaa-d1,mens,NCAA D1,Penn State,Big Ten Conference,1,1,1,1,1,1
wrestling,ncaa-d1,mens,NCAA D1,Iowa,Big Ten Conference,2,2,2,2,2,2
wrestling,ncaa-d1,mens,NCAA D1,Oklahoma State,Big 12 Conference,1,1,1,1,1,1
wrestling,ncaa-d2,mens,NCAA D2,Nebraska-Kearney,RMAC,1,1,1,2,1,1
wrestling,ncaa-d2,mens,NCAA D2,St. Cloud State,NSIC,1,1,2,1,2,1
```

**Field Definitions:**
- `Sport`: `wrestling`
- `Division`: `ncaa-d1`, `ncaa-d2`, or `ncaa-d3`
- `Gender`: `mens` or `womens`
- `College Division`: `NCAA D1`, `NCAA D2`, or `NCAA D3` (for display purposes)
- `School`: Full school name
- `Region`: Conference name (e.g., "Big Ten Conference", "RMAC")
- Year columns: Conference tournament placement (1-10+)

### Adding NCAA Data to Sorted CSV

```csv
Sport,Division,Gender,Year,Conference,Place,School
wrestling,ncaa-d1,mens,2024,Big Ten Conference,1,Penn State
wrestling,ncaa-d1,mens,2024,Big Ten Conference,2,Iowa
wrestling,ncaa-d1,mens,2024,Big Ten Conference,3,Michigan
wrestling,ncaa-d1,mens,2024,Big 12 Conference,1,Oklahoma State
wrestling,ncaa-d2,mens,2024,RMAC,1,Nebraska-Kearney
wrestling,ncaa-d2,mens,2024,RMAC,2,Colorado Mesa
```

## Scraping NCAA Data

### Option 1: Manual Entry

For NCAA data, manual entry may be most reliable due to:
- Varied website structures across conferences
- Different data formats
- Authentication requirements on some sites

**Process:**
1. Visit conference website or NCAA championship results
2. Find final conference standings or tournament results
3. Add to CSV files manually
4. Run `update_csv_structure.py` if needed to validate format

### Option 2: Custom Scrapers

Create specialized scrapers for NCAA conferences:

**Example: Big Ten Conference Scraper**
```python
# scraper_ncaa_big10.py
from web_parser import fetch_page, parse_html
from csv_handler import read_csv, write_csv

def scrape_big10_wrestling(year):
    """Scrape Big Ten wrestling standings"""
    url = f"https://bigten.org/sports/wrestling/standings/{year}"
    html = fetch_page(url)
    soup = parse_html(html)

    # Parse standings (structure varies by conference)
    standings = []
    # ... parsing logic ...

    return standings
```

### Option 3: API Integration

Some services provide APIs:
- **TrackWrestling API**: May provide programmatic access
- **NCAA Stats API**: Check for available endpoints
- Contact conference offices for data feeds

## Testing NCAA Data

After adding NCAA data:

1. **Verify CSV Format**:
   ```bash
   python3 -c "
   import csv
   with open('NAIA_blank - NAIA_results.csv') as f:
       reader = csv.DictReader(f)
       ncaa_rows = [r for r in reader if r['Division'].startswith('ncaa')]
       print(f'NCAA rows: {len(ncaa_rows)}')
   "
   ```

2. **Test API Endpoints**:
   ```bash
   # Get NCAA D1 schools
   curl "http://localhost:8080/api/v1/schools?sport=wrestling&division=ncaa-d1&gender=mens"

   # Get Big Ten standings for 2024
   curl "http://localhost:8080/api/v1/standings/2024?sport=wrestling&division=ncaa-d1" | jq '.[] | select(.conference | contains("Big Ten"))'

   # Export NCAA D1 data as CSV
   curl "http://localhost:8080/api/v1/export/csv?sport=wrestling&division=ncaa-d1&gender=mens&format=sorted" -o ncaa_d1_wrestling.csv
   ```

3. **Verify Statistics**:
   ```bash
   curl "http://localhost:8080/api/v1/stats?sport=wrestling&division=ncaa-d1&gender=mens"
   ```

## Example: Adding 2024 NCAA D1 Big Ten Wrestling

### Step 1: Find Data

Visit: https://bigten.org/sports/wrestling/standings/2024

### Step 2: Add to Main CSV

```csv
wrestling,ncaa-d1,mens,NCAA D1,Penn State,Big Ten Conference,,,,,,1
wrestling,ncaa-d1,mens,NCAA D1,Iowa,Big Ten Conference,,,,,,2
wrestling,ncaa-d1,mens,NCAA D1,Michigan,Big Ten Conference,,,,,,3
wrestling,ncaa-d1,mens,NCAA D1,Nebraska,Big Ten Conference,,,,,,4
wrestling,ncaa-d1,mens,NCAA D1,Ohio State,Big Ten Conference,,,,,,5
wrestling,ncaa-d1,mens,NCAA D1,Wisconsin,Big Ten Conference,,,,,,6
wrestling,ncaa-d1,mens,NCAA D1,Northwestern,Big Ten Conference,,,,,,7
wrestling,ncaa-d1,mens,NCAA D1,Minnesota,Big Ten Conference,,,,,,8
wrestling,ncaa-d1,mens,NCAA D1,Rutgers,Big Ten Conference,,,,,,9
wrestling,ncaa-d1,mens,NCAA D1,Illinois,Big Ten Conference,,,,,,10
```

### Step 3: Add to Sorted CSV

```csv
wrestling,ncaa-d1,mens,2024,Big Ten Conference,1,Penn State
wrestling,ncaa-d1,mens,2024,Big Ten Conference,2,Iowa
wrestling,ncaa-d1,mens,2024,Big Ten Conference,3,Michigan
wrestling,ncaa-d1,mens,2024,Big Ten Conference,4,Nebraska
wrestling,ncaa-d1,mens,2024,Big Ten Conference,5,Ohio State
wrestling,ncaa-d1,mens,2024,Big Ten Conference,6,Wisconsin
wrestling,ncaa-d1,mens,2024,Big Ten Conference,7,Northwestern
wrestling,ncaa-d1,mens,2024,Big Ten Conference,8,Minnesota
wrestling,ncaa-d1,mens,2024,Big Ten Conference,9,Rutgers
wrestling,ncaa-d1,mens,2024,Big Ten Conference,10,Illinois
```

### Step 4: Deploy

```bash
git add "NAIA_blank - NAIA_results.csv" NAIA_Complete_Sorted.csv
git commit -m "Add NCAA D1 Big Ten wrestling standings for 2024"
git push origin main
```

The API will automatically deploy and the new data will be available at:
```
https://api.athletehub.lanternbrp.com/api/v1/standings/2024?sport=wrestling&division=ncaa-d1
```

## Quick Reference

### API Queries for NCAA Data

**Get all NCAA D1 wrestling schools:**
```
GET /api/v1/schools?sport=wrestling&division=ncaa-d1&gender=mens
```

**Get NCAA D1 conferences:**
```
GET /api/v1/conferences?sport=wrestling&division=ncaa-d1&gender=mens
```

**Get 2024 NCAA D1 standings:**
```
GET /api/v1/standings/2024?sport=wrestling&division=ncaa-d1&gender=mens
```

**Get Big Ten standings for all years:**
```
GET /api/v1/conferences/Big%20Ten/standings?sport=wrestling&division=ncaa-d1&gender=mens
```

**Export NCAA D2 data as CSV:**
```
GET /api/v1/export/csv?sport=wrestling&division=ncaa-d2&gender=mens&format=sorted
```

### Division Codes

| Division | Code | Description |
|----------|------|-------------|
| NAIA | `naia` | National Association of Intercollegiate Athletics |
| NCAA D1 | `ncaa-d1` | NCAA Division I |
| NCAA D2 | `ncaa-d2` | NCAA Division II |
| NCAA D3 | `ncaa-d3` | NCAA Division III |

### Recommended Data Collection Strategy

**Phase 1: Major D1 Conferences (2020-2025)**
- Big Ten Conference
- Big 12 Conference
- ACC (Atlantic Coast Conference)

**Phase 2: Additional D1 Conferences**
- EIWA (Eastern Intercollegiate Wrestling Association)
- MAC (Mid-American Conference)
- Pac-12 Conference
- SoCon (Southern Conference)

**Phase 3: D2 Conferences**
- RMAC (Rocky Mountain Athletic Conference)
- NSIC (Northern Sun Intercollegiate Conference)
- MIAA (Mid-America Intercollegiate Athletics Association)
- PSAC (Pennsylvania State Athletic Conference)

**Phase 4: D3 Regional Data**
- National tournament qualifiers by region

## Notes

- NCAA conference standings may change mid-season
- Focus on end-of-season conference tournament results for accuracy
- Some schools may compete in multiple tournaments
- Conference membership changes over time (track conference realignment)
- Women's wrestling is growing rapidly at NCAA level - consider adding women's data

## Resources

- **NCAA Wrestling**: https://www.ncaa.com/sports/wrestling
- **Big Ten Wrestling**: https://bigten.org/sports/wrestling
- **TrackWrestling**: https://www.trackwrestling.com/
- **FloWrestling Rankings**: https://www.flowrestling.org/rankings
- **WrestleStat**: https://wrestlestat.com/ (advanced statistics)
