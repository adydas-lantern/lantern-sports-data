"""
Web scraping module for parsing website content.
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List, Any


class WebParser:
    """A class for parsing and scraping web pages."""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the WebParser.

        Args:
            base_url: Optional base URL for relative URL resolution
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from a URL.

        Args:
            url: The URL to fetch

        Returns:
            HTML content as string, or None if request fails
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_html(self, html: str, parser: str = 'lxml') -> BeautifulSoup:
        """
        Parse HTML content into BeautifulSoup object.

        Args:
            html: HTML content as string
            parser: Parser to use (default: 'lxml')

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, parser)

    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a URL in one step.

        Args:
            url: The URL to fetch and parse

        Returns:
            BeautifulSoup object, or None if fetch fails
        """
        html = self.fetch_page(url)
        if html:
            return self.parse_html(html)
        return None

    def extract_table(self, soup: BeautifulSoup, table_id: Optional[str] = None,
                     table_class: Optional[str] = None) -> List[List[str]]:
        """
        Extract table data from HTML.

        Args:
            soup: BeautifulSoup object
            table_id: ID of the table to extract
            table_class: Class of the table to extract

        Returns:
            List of rows, where each row is a list of cell values
        """
        if table_id:
            table = soup.find('table', id=table_id)
        elif table_class:
            table = soup.find('table', class_=table_class)
        else:
            table = soup.find('table')

        if not table:
            return []

        rows = []
        for tr in table.find_all('tr'):
            cells = [cell.get_text(strip=True) for cell in tr.find_all(['td', 'th'])]
            if cells:
                rows.append(cells)

        return rows

    def extract_links(self, soup: BeautifulSoup, selector: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Extract links from HTML.

        Args:
            soup: BeautifulSoup object
            selector: CSS selector to filter links (optional)

        Returns:
            List of dictionaries with 'text' and 'href' keys
        """
        if selector:
            links = soup.select(selector)
        else:
            links = soup.find_all('a')

        return [
            {'text': link.get_text(strip=True), 'href': link.get('href', '')}
            for link in links if link.get('href')
        ]

    def extract_by_selector(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """
        Extract elements by CSS selector.

        Args:
            soup: BeautifulSoup object
            selector: CSS selector

        Returns:
            List of text content from matching elements
        """
        elements = soup.select(selector)
        return [elem.get_text(strip=True) for elem in elements]
