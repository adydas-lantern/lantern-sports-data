"""
NAIA Wrestling Standings Scraper module.
"""
import os
import json
import re
from typing import Dict, List, Optional, Set
from pathlib import Path
from dotenv import load_dotenv
from web_parser import WebParser
from csv_handler import CSVHandler


class NAIAScraper:
    """A class for scraping NAIA wrestling standings data."""

    def __init__(self, csv_file: str = "NAIA_blank - NAIA_results.csv"):
        """
        Initialize the NAIA Scraper.

        Args:
            csv_file: Path to the CSV file containing school data
        """
        load_dotenv()
        self.csv_file = csv_file
        self.parser = WebParser()
        self.csv_handler = CSVHandler()
        self.processed_urls_file = "processed_urls.json"
        self.processed_urls = self._load_processed_urls()

    def _load_processed_urls(self) -> Set[str]:
        """
        Load the set of already processed URLs from file.

        Returns:
            Set of processed URLs
        """
        if os.path.exists(self.processed_urls_file):
            try:
                with open(self.processed_urls_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('urls', []))
            except Exception as e:
                print(f"Error loading processed URLs: {e}")
                return set()
        return set()

    def _save_processed_urls(self):
        """Save the set of processed URLs to file."""
        try:
            with open(self.processed_urls_file, 'w') as f:
                json.dump({'urls': list(self.processed_urls)}, f, indent=2)
            print(f"Saved {len(self.processed_urls)} processed URLs")
        except Exception as e:
            print(f"Error saving processed URLs: {e}")

    def is_url_processed(self, url: str) -> bool:
        """
        Check if a URL has already been processed.

        Args:
            url: URL to check

        Returns:
            True if URL has been processed, False otherwise
        """
        return url in self.processed_urls

    def mark_url_processed(self, url: str):
        """
        Mark a URL as processed.

        Args:
            url: URL to mark as processed
        """
        self.processed_urls.add(url)
        self._save_processed_urls()

    def get_school_data(self) -> List[Dict[str, str]]:
        """
        Load school data from CSV file.

        Returns:
            List of dictionaries containing school information
        """
        data = self.csv_handler.read_csv_as_dicts(self.csv_file)
        return data

    def scrape_standings(self, url: str, year: int) -> Dict[str, any]:
        """
        Scrape wrestling standings from a given URL for a specific year.

        Args:
            url: URL to scrape
            year: Year of the standings (2020-2025)

        Returns:
            Dictionary with scraped data
        """
        # Check if URL already processed
        if self.is_url_processed(url):
            print(f"URL already processed: {url}")
            return {'status': 'skipped', 'url': url, 'reason': 'already_processed'}

        print(f"Scraping standings for {year} from: {url}")

        soup = self.parser.get_soup(url)
        if not soup:
            print(f"Failed to fetch page: {url}")
            return {'status': 'failed', 'url': url, 'reason': 'fetch_failed'}

        # Extract standings data
        standings_data = self._extract_standings(soup, year)

        # Mark URL as processed
        self.mark_url_processed(url)

        return {
            'status': 'success',
            'url': url,
            'year': year,
            'data': standings_data
        }

    def _parse_standings_text_dash_format(self, text: str) -> List[Dict[str, str]]:
        """
        Parse standings text in dash-separated format (used in 2024-25 and earlier).
        Format: "School1 - Score1School2 - Score2..." or "1. School1 - Score1 2. School2 - Score2..."

        Args:
            text: Raw standings text

        Returns:
            List of dictionaries with rank, school, score
        """
        standings = []

        # Check if format includes rank numbers (e.g., "1. School - Score")
        if re.search(r'^\d+\.\s+\w+', text.strip()):
            # Tournament format: "1. School - Score 2. School - Score..."
            # Split by rank pattern (digit followed by period and space)
            entries = re.split(r'\d+\.\s+', text)
            entries = [e.strip() for e in entries if e.strip()]

            for entry in entries:
                # Parse "School - Score" format
                match = re.match(r'^(.+?)\s*-\s*(\d+\.?\d*)$', entry)
                if match:
                    school = match.group(1).strip()
                    score = match.group(2)
                    rank = str(len(standings) + 1)
                    standings.append({
                        'rank': rank,
                        'school': school,
                        'score': score
                    })
        else:
            # Original format: "School1 - Score1School2 - Score2..."
            # Split by numbers (scores), keeping the numbers
            parts = re.split(r'(\d+\.?\d*)', text)
            parts = [p.strip() for p in parts if p.strip() and p.strip() != '-']

            # Process in pairs: school, score
            for i in range(0, len(parts) - 1, 2):
                school_with_dash = parts[i]
                score = parts[i + 1]

                # Remove trailing dash from school name
                school = school_with_dash.rstrip(' -').strip()

                if school:
                    rank = str(len(standings) + 1)
                    standings.append({
                        'rank': rank,
                        'school': school,
                        'score': score
                    })

        return standings

    def _parse_standings_text(self, text: str) -> List[Dict[str, str]]:
        """
        Parse standings text in NAIA format.
        Format: "1 School1 2162 School2 1983 School3..."

        Args:
            text: Raw standings text

        Returns:
            List of dictionaries with rank, school, score
        """
        standings = []

        # Detect format: check if text contains " - " pattern
        if ' - ' in text[:100]:  # Check first 100 chars
            return self._parse_standings_text_dash_format(text)

        # Insert delimiter before "digit(s) space uppercase-letter"
        delimited = re.sub(r'(\d)\s+([A-Z])', r'\1||\2', text)

        # Split by delimiter
        entries = [e.strip() for e in delimited.split('||') if e.strip()]

        for i, entry in enumerate(entries):
            # Skip if entry is just digits (first entry's rank)
            if entry.isdigit():
                continue

            # Pattern: school name followed by 3-4 digits
            match = re.match(r'^(.+?)\s+(\d{2,4})$', entry)
            if match:
                school = match.group(1).strip()
                score_combo = match.group(2)

                # Determine rank - look at previous entry
                if i > 0 and entries[i-1].isdigit():
                    rank = entries[i-1]
                else:
                    # Rank might be sequential
                    rank = str(len(standings) + 1)

                # Split score_combo if it's 4 digits (score + next rank)
                if len(score_combo) == 4:
                    score = score_combo[:3]
                else:
                    score = score_combo

                standings.append({
                    'rank': rank,
                    'school': school,
                    'score': score
                })

        return standings

    def _extract_standings(self, soup, year: int) -> List[Dict[str, str]]:
        """
        Extract standings data from parsed HTML.

        Args:
            soup: BeautifulSoup object
            year: Year of the standings

        Returns:
            List of dictionaries with school standings including conference info
        """
        all_standings = []

        # Find all conference headers (in <strong> tags)
        conf_headers = soup.find_all('strong', string=lambda text: text and 'Conference' in text)

        print(f"Found {len(conf_headers)} conference sections")

        for conf in conf_headers:
            conf_name = conf.get_text(strip=True)

            # Check if there's a previous <strong> tag to combine (e.g., "Cas" + "cade Conference")
            prev_strong = conf.find_previous_sibling('strong')
            if prev_strong:
                prev_text = prev_strong.get_text(strip=True)
                # If previous strong tag is short (< 10 chars) and right before this one, combine them
                if len(prev_text) < 10 and 'Conference' not in prev_text:
                    conf_name = prev_text + conf_name

            # Get the paragraph containing standings data
            current = conf.parent
            next_p = current.find_next_sibling('p')

            if not next_p:
                next_p = current.find_next('p')

            if next_p:
                standings_text = next_p.get_text(strip=True)

                # Skip if it's a header or empty
                if 'Conference' in standings_text or len(standings_text) < 10:
                    continue

                # Remove "Individual Rankings" suffix if present
                if 'Individual Rankings' in standings_text:
                    standings_text = standings_text.split('Individual Rankings')[0].strip()

                # Parse the standings text
                standings = self._parse_standings_text(standings_text)

                # Add conference info and year to each standing
                for standing in standings:
                    standing['conference'] = conf_name
                    standing['year'] = year
                    standing['place'] = standing['rank']  # CSV uses 'place'
                    all_standings.append(standing)

                print(f"  {conf_name}: {len(standings)} schools")

        return all_standings

    def update_csv_with_standings(self, standings_data: List[Dict[str, str]], year: int):
        """
        Update the CSV file with scraped standings data.

        Args:
            standings_data: List of dictionaries with standings
            year: Year of the standings
        """
        # Load current CSV data
        csv_data = self.csv_handler.read_csv(self.csv_file)
        headers = csv_data['headers']
        rows = csv_data['rows']

        # Find the column index for the year
        year_column_name = f"{year} Conference Team Place"
        if year_column_name not in headers:
            print(f"Warning: Column '{year_column_name}' not found in CSV")
            return

        year_col_index = headers.index(year_column_name)

        # Update rows with standings
        for standing in standings_data:
            school_name = standing.get('school', '')
            place = standing.get('place', '')

            # Find matching row in CSV (match school name)
            for i, row in enumerate(rows):
                if len(row) > 1:  # Ensure row has school name column
                    csv_school = row[1]  # Column B (index 1) is school name

                    # Match school name (case-insensitive, partial match)
                    if school_name.lower() in csv_school.lower() or csv_school.lower() in school_name.lower():
                        # Update the year column with the place
                        while len(row) <= year_col_index:
                            row.append('')
                        row[year_col_index] = place
                        print(f"Updated {csv_school} - {year}: {place}")
                        break

        # Write updated data back to CSV
        self.csv_handler.write_csv(self.csv_file, headers, rows)
        print(f"CSV updated with {year} standings")

    def scrape_from_env(self):
        """
        Scrape using the URL from .env file.
        """
        start_url = os.getenv('NAIA_START_URL')

        if not start_url:
            print("Error: NAIA_START_URL not found in .env file")
            print("Please add the URL to the .env file")
            return

        # Extract year from URL or prompt for it
        # For now, we'll need to specify the year
        print(f"Starting URL: {start_url}")
        print("You'll need to specify the year when calling scrape_standings()")

    def get_processed_urls(self) -> List[str]:
        """
        Get list of all processed URLs.

        Returns:
            List of processed URLs
        """
        return list(self.processed_urls)

    def clear_processed_urls(self):
        """Clear the list of processed URLs (use with caution)."""
        self.processed_urls.clear()
        self._save_processed_urls()
        print("Cleared all processed URLs")
