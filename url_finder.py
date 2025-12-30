"""
URL Finder module for discovering NAIA wrestling standings URLs.
Uses Google search to find standings pages for different years.
"""
import re
from typing import List, Dict, Optional
from web_parser import WebParser


class URLFinder:
    """A class for finding NAIA wrestling standings URLs via search."""

    def __init__(self):
        """Initialize the URL Finder."""
        self.parser = WebParser()
        self.found_urls = {}

    def search_google_for_urls(self, query: str) -> List[str]:
        """
        Search Google and extract URLs from results.

        Note: This is a placeholder. In production, you would use:
        - Google Custom Search API
        - SerpAPI
        - Or the WebSearch tool if available

        Args:
            query: Search query string

        Returns:
            List of URLs found in search results
        """
        # This is a placeholder - actual implementation would use WebSearch tool
        # or an API like SerpAPI/Google Custom Search API
        print(f"Would search Google for: {query}")
        return []

    def find_naia_standings_urls(self, year: int) -> List[str]:
        """
        Find NAIA wrestling standings URLs for a specific year.

        Args:
            year: Year to search for (2020-2025)

        Returns:
            List of potential standings URLs
        """
        # Convert year to NAIA season format (e.g., 2024 -> 2024-25)
        if year >= 2025:
            season = f"{year}-{str(year+1)[-2:]}"
        else:
            season = f"{year}-{str(year+1)[-2:]}"

        print(f"\nSearching for {season} season...")

        # Try to directly construct potential URLs
        potential_urls = [
            f"https://www.naia.org/sports/mwrest/{season}/Releases/Conf",
            f"https://www.naia.org/sports/mwrest/{season}/Releases/Conf_1",
            f"https://www.naia.org/sports/mwrest/{season}/releases/conf",
            f"https://www.naia.org/sports/mwrest/{season}/standings",
        ]

        # Test which URLs are valid
        valid_urls = []
        for url in potential_urls:
            print(f"Testing: {url}")
            soup = self.parser.get_soup(url)
            if soup:
                # Check if page has conference standings data
                if self._has_standings_data(soup):
                    print(f"  ✓ Found valid standings page!")
                    valid_urls.append(url)
                else:
                    print(f"  ✗ Page exists but no standings data")
            else:
                print(f"  ✗ URL not found")

        return valid_urls

    def _has_standings_data(self, soup) -> bool:
        """
        Check if a page contains standings data.

        Args:
            soup: BeautifulSoup object

        Returns:
            True if page has standings data
        """
        # Look for conference headers
        conf_headers = soup.find_all('strong', string=lambda text: text and 'Conference' in text)

        # Look for keywords in page content
        page_text = soup.get_text().lower()
        has_keywords = any(keyword in page_text for keyword in [
            'conference rating',
            'conference team',
            'standings',
            'team place'
        ])

        return len(conf_headers) > 0 or has_keywords

    def find_all_years(self, start_year: int = 2020, end_year: int = 2025) -> Dict[int, List[str]]:
        """
        Find standings URLs for multiple years.

        Args:
            start_year: Starting year (default 2020)
            end_year: Ending year (default 2025)

        Returns:
            Dictionary mapping year to list of URLs
        """
        results = {}

        for year in range(start_year, end_year + 1):
            urls = self.find_naia_standings_urls(year)
            if urls:
                results[year] = urls
                print(f"\n✓ Found {len(urls)} URL(s) for {year}")
            else:
                print(f"\n✗ No URLs found for {year}")

        return results

    def explore_site_structure(self, base_url: str) -> List[str]:
        """
        Explore a NAIA site section to find standings pages.

        Args:
            base_url: Base URL to explore (e.g., https://www.naia.org/sports/mwrest/2024-25)

        Returns:
            List of found standings URLs
        """
        print(f"\nExploring: {base_url}")

        soup = self.parser.get_soup(base_url)
        if not soup:
            print("Failed to fetch page")
            return []

        # Find all links on the page
        links = self.parser.extract_links(soup)

        # Filter for links that might be standings
        standings_links = []
        for link in links:
            href = link.get('href', '')
            text = link.get('text', '').lower()

            # Look for links with keywords
            if any(keyword in text for keyword in ['rating', 'standing', 'conference', 'team']):
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    href = 'https://www.naia.org' + href
                elif not href.startswith('http'):
                    href = base_url + '/' + href

                standings_links.append({
                    'url': href,
                    'text': text
                })

        print(f"Found {len(standings_links)} potential links")
        for link in standings_links[:10]:  # Show first 10
            print(f"  - {link['text']}: {link['url']}")

        return [link['url'] for link in standings_links]

    def get_year_from_url(self, url: str) -> Optional[int]:
        """
        Extract year from a NAIA URL.

        Args:
            url: URL to parse

        Returns:
            Year as integer, or None if not found
        """
        # Look for pattern like "2024-25" or "2024"
        match = re.search(r'/(\d{4})-\d{2}/', url)
        if match:
            return int(match.group(1))

        match = re.search(r'/(\d{4})/', url)
        if match:
            return int(match.group(1))

        return None

    def save_urls_to_file(self, urls_by_year: Dict[int, List[str]], filename: str = "found_urls.txt"):
        """
        Save found URLs to a file.

        Args:
            urls_by_year: Dictionary of year -> URLs
            filename: Output filename
        """
        with open(filename, 'w') as f:
            f.write("# NAIA Wrestling Standings URLs\n")
            f.write("# Found by URL Finder\n\n")

            for year in sorted(urls_by_year.keys()):
                urls = urls_by_year[year]
                f.write(f"# Year: {year}\n")
                for url in urls:
                    f.write(f"{url}\n")
                f.write("\n")

        print(f"\nSaved URLs to {filename}")
