#!/usr/bin/env python3
"""
Update CSV files to include Sport, Division, and Gender columns
"""
import csv

def update_csv(input_file, output_file, csv_type='main'):
    """Add sport, division, gender columns to CSV"""
    with open(input_file, 'r', encoding='utf-8') as f_in:
        reader = csv.DictReader(f_in)
        rows = list(reader)

    if csv_type == 'main':
        # New fieldnames with sport, division, gender at the beginning
        fieldnames = [
            'Sport',
            'Division',
            'Gender',
            'College Division',  # Keep for backward compat
            'School',
            'Region',
            '2020 Conference Team Place',
            '2021 Conference Team Place',
            '2022 Conference Team Place',
            '2023 Conference Team Place',
            '2024 Conference Team Place',
            '2025 Conference Team Place'
        ]
    else:  # sorted CSV
        fieldnames = [
            'Sport',
            'Division',
            'Gender',
            'Year',
            'Conference',
            'Place',
            'School'
        ]

    # Update each row
    for row in rows:
        row['Sport'] = 'wrestling'
        row['Division'] = 'naia'
        row['Gender'] = 'mens'

    # Write updated CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Updated {len(rows)} rows")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")

if __name__ == '__main__':
    # Update main CSV
    update_csv(
        'NAIA_blank - NAIA_results.csv',
        'NAIA_blank - NAIA_results.csv.new',
        csv_type='main'
    )

    # Update sorted CSV
    update_csv(
        'NAIA_Complete_Sorted.csv',
        'NAIA_Complete_Sorted.csv.new',
        csv_type='sorted'
    )

    print("\n✓ CSV files updated!")
    print("  Review the .new files, then:")
    print("  mv 'NAIA_blank - NAIA_results.csv.new' 'NAIA_blank - NAIA_results.csv'")
    print("  mv NAIA_Complete_Sorted.csv.new NAIA_Complete_Sorted.csv")
