"""
Data loader utilities for reading CSV data
"""
import csv
from typing import List, Dict, Optional
from pathlib import Path
from api.models import School, Standing, Conference, SchoolPlacement, ConferenceStandings


class DataLoader:
    """Loads and manages NAIA wrestling data from CSV files"""

    def __init__(self, main_csv_path: str, sorted_csv_path: str):
        self.main_csv_path = Path(main_csv_path)
        self.sorted_csv_path = Path(sorted_csv_path)
        self.schools_data: List[Dict] = []
        self.standings_data: List[Standing] = []
        self.conferences_cache: Dict[str, Conference] = {}
        self.loaded = False

    def load_data(self) -> bool:
        """Load data from CSV files"""
        try:
            # Load main CSV for school details
            with open(self.main_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.schools_data = list(reader)

            # Load sorted CSV for standings
            with open(self.sorted_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                standings_rows = list(reader)

            self.standings_data = [
                Standing(
                    year=int(row['Year']),
                    conference=row['Conference'],
                    place=int(row['Place']),
                    school=row['School']
                )
                for row in standings_rows
            ]

            # Build conferences cache
            self._build_conferences_cache()

            self.loaded = True
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def _build_conferences_cache(self):
        """Build cache of conferences from standings data"""
        conf_schools: Dict[str, set] = {}
        conf_years: Dict[str, set] = {}

        for standing in self.standings_data:
            conf_name = standing.conference

            if conf_name not in conf_schools:
                conf_schools[conf_name] = set()
                conf_years[conf_name] = set()

            conf_schools[conf_name].add(standing.school)
            conf_years[conf_name].add(standing.year)

        self.conferences_cache = {
            name: Conference(
                name=name,
                schools=sorted(list(schools)),
                years_active=sorted(list(conf_years[name]))
            )
            for name, schools in conf_schools.items()
        }

    def get_all_schools(self) -> List[School]:
        """Get all schools with their placements"""
        schools = []

        for row in self.schools_data:
            school_name = row['School']
            conference = row['Region']

            # Get all placements for this school
            placements = []
            for year in [2020, 2021, 2022, 2023, 2024, 2025]:
                place_str = row.get(f'{year} Conference Team Place', '').strip()
                if place_str:
                    placements.append(SchoolPlacement(
                        year=year,
                        place=int(place_str),
                        conference=conference
                    ))

            schools.append(School(
                name=school_name,
                division=row['College Division'],
                conference=conference,
                placements=placements
            ))

        return schools

    def get_school_by_name(self, name: str) -> Optional[School]:
        """Get a specific school by name (case-insensitive partial match)"""
        name_lower = name.lower()

        for row in self.schools_data:
            school_name = row['School']
            if name_lower in school_name.lower() or school_name.lower() in name_lower:
                conference = row['Region']

                # Get all placements for this school
                placements = []
                for year in [2020, 2021, 2022, 2023, 2024, 2025]:
                    place_str = row.get(f'{year} Conference Team Place', '').strip()
                    if place_str:
                        placements.append(SchoolPlacement(
                            year=year,
                            place=int(place_str),
                            conference=conference
                        ))

                return School(
                    name=school_name,
                    division=row['College Division'],
                    conference=conference,
                    placements=placements
                )

        return None

    def get_all_conferences(self) -> List[Conference]:
        """Get all conferences"""
        return list(self.conferences_cache.values())

    def get_conference_by_name(self, name: str) -> Optional[Conference]:
        """Get a specific conference by name (case-insensitive partial match)"""
        name_lower = name.lower()

        for conf_name, conference in self.conferences_cache.items():
            if name_lower in conf_name.lower() or conf_name.lower() in name_lower:
                return conference

        return None

    def get_standings_by_year(self, year: int) -> List[Standing]:
        """Get all standings for a specific year"""
        return [s for s in self.standings_data if s.year == year]

    def get_standings_by_year_and_conference(
        self,
        year: int,
        conference: str
    ) -> Optional[ConferenceStandings]:
        """Get standings for a specific year and conference"""
        conf_lower = conference.lower()

        # Find matching conference name
        matching_conf = None
        for standing in self.standings_data:
            if conf_lower in standing.conference.lower():
                matching_conf = standing.conference
                break

        if not matching_conf:
            return None

        standings = [
            s for s in self.standings_data
            if s.year == year and s.conference == matching_conf
        ]

        if not standings:
            return None

        # Sort by place
        standings.sort(key=lambda x: x.place)

        return ConferenceStandings(
            year=year,
            conference=matching_conf,
            standings=standings
        )

    def get_conference_standings(self, conference: str) -> Dict[int, List[Standing]]:
        """Get all standings for a conference, grouped by year"""
        conf_lower = conference.lower()

        # Find matching conference name
        matching_conf = None
        for standing in self.standings_data:
            if conf_lower in standing.conference.lower():
                matching_conf = standing.conference
                break

        if not matching_conf:
            return {}

        result: Dict[int, List[Standing]] = {}

        for standing in self.standings_data:
            if standing.conference == matching_conf:
                if standing.year not in result:
                    result[standing.year] = []
                result[standing.year].append(standing)

        # Sort standings within each year
        for year in result:
            result[year].sort(key=lambda x: x.place)

        return result

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        return {
            "total_schools": len(self.schools_data),
            "total_standings": len(self.standings_data),
            "total_conferences": len(self.conferences_cache),
            "years_covered": len(set(s.year for s in self.standings_data))
        }
