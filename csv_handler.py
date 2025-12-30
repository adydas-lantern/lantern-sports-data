"""
CSV parsing and creation module.
"""
import csv
from typing import List, Dict, Any, Optional
from pathlib import Path


class CSVHandler:
    """A class for reading, writing, and manipulating CSV files."""

    @staticmethod
    def read_csv(file_path: str, has_header: bool = True) -> Dict[str, Any]:
        """
        Read CSV file and return data.

        Args:
            file_path: Path to the CSV file
            has_header: Whether the CSV has a header row

        Returns:
            Dictionary with 'headers' and 'rows' keys
        """
        data = {'headers': [], 'rows': []}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)

                if has_header:
                    data['headers'] = next(reader, [])

                data['rows'] = list(reader)

            print(f"Successfully read {len(data['rows'])} rows from {file_path}")
            return data

        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")
            return data
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return data

    @staticmethod
    def read_csv_as_dicts(file_path: str) -> List[Dict[str, str]]:
        """
        Read CSV file and return rows as dictionaries.

        Args:
            file_path: Path to the CSV file

        Returns:
            List of dictionaries, where keys are column headers
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            print(f"Successfully read {len(rows)} rows from {file_path}")
            return rows

        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")
            return []
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return []

    @staticmethod
    def write_csv(file_path: str, headers: List[str], rows: List[List[Any]],
                  mode: str = 'w') -> bool:
        """
        Write data to CSV file.

        Args:
            file_path: Path to the CSV file
            headers: List of column headers
            rows: List of rows (each row is a list of values)
            mode: File mode ('w' for write, 'a' for append)

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, mode, encoding='utf-8', newline='') as f:
                writer = csv.writer(f)

                if mode == 'w' and headers:
                    writer.writerow(headers)

                writer.writerows(rows)

            print(f"Successfully wrote {len(rows)} rows to {file_path}")
            return True

        except Exception as e:
            print(f"Error writing CSV: {e}")
            return False

    @staticmethod
    def write_csv_from_dicts(file_path: str, rows: List[Dict[str, Any]],
                            fieldnames: Optional[List[str]] = None,
                            mode: str = 'w') -> bool:
        """
        Write dictionaries to CSV file.

        Args:
            file_path: Path to the CSV file
            rows: List of dictionaries
            fieldnames: List of field names (uses keys from first row if not provided)
            mode: File mode ('w' for write, 'a' for append)

        Returns:
            True if successful, False otherwise
        """
        if not rows:
            print("No data to write")
            return False

        if fieldnames is None:
            fieldnames = list(rows[0].keys())

        try:
            with open(file_path, mode, encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                if mode == 'w':
                    writer.writeheader()

                writer.writerows(rows)

            print(f"Successfully wrote {len(rows)} rows to {file_path}")
            return True

        except Exception as e:
            print(f"Error writing CSV: {e}")
            return False

    @staticmethod
    def append_row(file_path: str, row: List[Any]) -> bool:
        """
        Append a single row to CSV file.

        Args:
            file_path: Path to the CSV file
            row: Row data as list

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            return True
        except Exception as e:
            print(f"Error appending row: {e}")
            return False

    @staticmethod
    def filter_rows(rows: List[Dict[str, Any]], column: str, value: Any) -> List[Dict[str, Any]]:
        """
        Filter rows based on column value.

        Args:
            rows: List of row dictionaries
            column: Column name to filter on
            value: Value to match

        Returns:
            Filtered list of rows
        """
        return [row for row in rows if row.get(column) == value]

    @staticmethod
    def sort_rows(rows: List[Dict[str, Any]], column: str, reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Sort rows by column value.

        Args:
            rows: List of row dictionaries
            column: Column name to sort by
            reverse: Sort in descending order if True

        Returns:
            Sorted list of rows
        """
        return sorted(rows, key=lambda x: x.get(column, ''), reverse=reverse)
