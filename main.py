"""
Main application entry point for web scraping and CSV handling.
"""
import os
from web_parser import WebParser
from csv_handler import CSVHandler
from naia_scraper import NAIAScraper


def example_web_scraping():
    """Example: Scrape a website and extract data."""
    print("\n=== Web Scraping Example ===")

    # Initialize parser
    parser = WebParser()

    # Example: Scrape a webpage
    url = "https://example.com"  # Replace with your target URL
    soup = parser.get_soup(url)

    if soup:
        # Extract tables
        tables = parser.extract_table(soup)
        print(f"Found table with {len(tables)} rows")

        # Extract links
        links = parser.extract_links(soup)
        print(f"Found {len(links)} links")
    else:
        print("Failed to fetch page")


def example_csv_operations():
    """Example: Read, manipulate, and write CSV data."""
    print("\n=== CSV Operations Example ===")

    handler = CSVHandler()

    # Read existing CSV
    csv_file = "NAIA_blank - NAIA_results.csv"
    data = handler.read_csv_as_dicts(csv_file)

    if data:
        print(f"Loaded {len(data)} rows")
        if data:
            print(f"Columns: {list(data[0].keys())}")

    # Create new CSV
    new_file = "output.csv"
    headers = ["Name", "Rank", "Score"]
    rows = [
        ["John Doe", "1", "95"],
        ["Jane Smith", "2", "92"],
        ["Bob Johnson", "3", "88"]
    ]

    handler.write_csv(new_file, headers, rows)


def example_scrape_to_csv():
    """Example: Scrape website and save to CSV."""
    print("\n=== Scrape to CSV Example ===")

    parser = WebParser()
    handler = CSVHandler()

    # Scrape website
    url = "https://example.com"  # Replace with your target URL
    soup = parser.get_soup(url)

    if soup:
        # Extract table data
        table_data = parser.extract_table(soup)

        if table_data:
            # Assume first row is headers
            headers = table_data[0]
            rows = table_data[1:]

            # Save to CSV
            output_file = "scraped_data.csv"
            handler.write_csv(output_file, headers, rows)
            print(f"Saved {len(rows)} rows to {output_file}")


def scrape_naia_wrestling():
    """Scrape NAIA wrestling standings and update CSV."""
    print("\n=== NAIA Wrestling Standings Scraper ===")

    scraper = NAIAScraper()

    # Check for start URL from .env
    start_url = os.getenv('NAIA_START_URL')

    if not start_url:
        print("\nERROR: Please add NAIA_START_URL to your .env file")
        print("Example: NAIA_START_URL=https://example.com/standings/2024")
        return

    print(f"Start URL: {start_url}")

    # Check if URL was already processed
    if scraper.is_url_processed(start_url):
        print(f"\nURL already processed: {start_url}")
        print("Skipping to avoid duplicate scraping.")
        print("\nProcessed URLs:")
        for url in scraper.get_processed_urls():
            print(f"  - {url}")
        return

    # Prompt for year (or extract from URL)
    print("\nWhich year are you scraping? (2020-2025)")
    year_input = input("Year: ").strip()

    try:
        year = int(year_input)
        if year < 2020 or year > 2025:
            print("Year must be between 2020 and 2025")
            return
    except ValueError:
        print("Invalid year")
        return

    # Scrape the standings
    result = scraper.scrape_standings(start_url, year)

    if result['status'] == 'success':
        print(f"\nSuccessfully scraped {len(result['data'])} standings")

        # Update CSV with the data
        scraper.update_csv_with_standings(result['data'], year)
        print(f"\nCSV updated with {year} standings")

        print("\nNext steps:")
        print("1. Update NAIA_START_URL in .env with next URL to scrape")
        print("2. Run the script again to scrape the next year/conference")
    else:
        print(f"\nFailed to scrape: {result.get('reason', 'unknown error')}")


def view_processed_urls():
    """View all processed URLs."""
    print("\n=== Processed URLs ===")
    scraper = NAIAScraper()
    urls = scraper.get_processed_urls()

    if urls:
        print(f"\nFound {len(urls)} processed URLs:")
        for i, url in enumerate(urls, 1):
            print(f"{i}. {url}")
    else:
        print("\nNo URLs have been processed yet")


def main():
    """Main function."""
    print("NAIA Wrestling Standing Scraper")
    print("=" * 50)

    # Uncomment the function you want to run:
    scrape_naia_wrestling()
    # view_processed_urls()
    # example_csv_operations()

    print("\n" + "=" * 50)
    print("Done!")


if __name__ == "__main__":
    main()
