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
                    sport=row.get('Sport', 'wrestling'),
                    division=row.get('Division', 'naia'),
                    gender=row.get('Gender', 'mens'),
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
        # Key: (conference_name, sport, division, gender)
        conf_data: Dict[tuple, Dict] = {}

        for standing in self.standings_data:
            key = (standing.conference, standing.sport, standing.division, standing.gender)

            if key not in conf_data:
                conf_data[key] = {
                    'schools': set(),
                    'years': set()
                }

            conf_data[key]['schools'].add(standing.school)
            conf_data[key]['years'].add(standing.year)

        self.conferences_cache = {
            f"{name}|{sport}|{division}|{gender}": Conference(
                name=name,
                sport=sport,
                division=division,
                gender=gender,
                schools=sorted(list(data['schools'])),
                years_active=sorted(list(data['years']))
            )
            for (name, sport, division, gender), data in conf_data.items()
        }

    def get_all_schools(self, sport: Optional[str] = None, division: Optional[str] = None, gender: Optional[str] = None) -> List[School]:
        """Get all schools with their placements, optionally filtered by sport/division/gender"""
        schools = []

        for row in self.schools_data:
            # Filter by sport/division/gender if specified
            row_sport = row.get('Sport', 'wrestling')
            row_division = row.get('Division', 'naia')
            row_gender = row.get('Gender', 'mens')

            if sport and row_sport != sport:
                continue
            if division and row_division != division:
                continue
            if gender and row_gender != gender:
                continue

            school_name = row['School']
            conference = row['Region']

            # Get all placements for this school
            placements = []
            for year in [2020, 2021, 2022, 2023, 2024, 2025]:
                place_str = row.get(f'{year} Conference Team Place', '').strip()
                if place_str:
                    placements.append(SchoolPlacement(
                        sport=row_sport,
                        division=row_division,
                        gender=row_gender,
                        year=year,
                        place=int(place_str),
                        conference=conference
                    ))

            schools.append(School(
                name=school_name,
                sport=row_sport,
                division=row_division,
                gender=row_gender,
                conference=conference,
                placements=placements
            ))

        return schools

    def get_school_by_name(self, name: str, sport: Optional[str] = None, division: Optional[str] = None, gender: Optional[str] = None) -> Optional[School]:
        """Get a specific school by name (case-insensitive partial match)"""
        name_lower = name.lower()

        for row in self.schools_data:
            school_name = row['School']
            if name_lower in school_name.lower() or school_name.lower() in name_lower:
                row_sport = row.get('Sport', 'wrestling')
                row_division = row.get('Division', 'naia')
                row_gender = row.get('Gender', 'mens')

                # Filter if specified
                if sport and row_sport != sport:
                    continue
                if division and row_division != division:
                    continue
                if gender and row_gender != gender:
                    continue

                conference = row['Region']

                # Get all placements for this school
                placements = []
                for year in [2020, 2021, 2022, 2023, 2024, 2025]:
                    place_str = row.get(f'{year} Conference Team Place', '').strip()
                    if place_str:
                        placements.append(SchoolPlacement(
                            sport=row_sport,
                            division=row_division,
                            gender=row_gender,
                            year=year,
                            place=int(place_str),
                            conference=conference
                        ))

                return School(
                    name=school_name,
                    sport=row_sport,
                    division=row_division,
                    gender=row_gender,
                    conference=conference,
                    placements=placements
                )

        return None

    def get_all_conferences(self, sport: Optional[str] = None, division: Optional[str] = None, gender: Optional[str] = None) -> List[Conference]:
        """Get all conferences, optionally filtered by sport/division/gender"""
        conferences = []
        for conf in self.conferences_cache.values():
            if sport and conf.sport != sport:
                continue
            if division and conf.division != division:
                continue
            if gender and conf.gender != gender:
                continue
            conferences.append(conf)
        return conferences

    def get_conference_by_name(self, name: str) -> Optional[Conference]:
        """Get a specific conference by name (case-insensitive partial match)"""
        name_lower = name.lower()

        for conf_name, conference in self.conferences_cache.items():
            if name_lower in conf_name.lower() or conf_name.lower() in name_lower:
                return conference

        return None

    def get_standings_by_year(self, year: int, sport: Optional[str] = None, division: Optional[str] = None, gender: Optional[str] = None) -> List[Standing]:
        """Get all standings for a specific year, optionally filtered"""
        standings = []
        for s in self.standings_data:
            if s.year != year:
                continue
            if sport and s.sport != sport:
                continue
            if division and s.division != division:
                continue
            if gender and s.gender != gender:
                continue
            standings.append(s)
        return standings

    def get_standings_by_year_and_conference(
        self,
        year: int,
        conference: str,
        sport: Optional[str] = None,
        division: Optional[str] = None,
        gender: Optional[str] = None
    ) -> Optional[ConferenceStandings]:
        """Get standings for a specific year and conference"""
        conf_lower = conference.lower()

        # Find matching conference name
        matching_standing = None
        for standing in self.standings_data:
            if conf_lower in standing.conference.lower():
                # Check filters
                if sport and standing.sport != sport:
                    continue
                if division and standing.division != division:
                    continue
                if gender and standing.gender != gender:
                    continue
                matching_standing = standing
                break

        if not matching_standing:
            return None

        standings = [
            s for s in self.standings_data
            if s.year == year
            and s.conference == matching_standing.conference
            and s.sport == matching_standing.sport
            and s.division == matching_standing.division
            and s.gender == matching_standing.gender
        ]

        if not standings:
            return None

        # Sort by place
        standings.sort(key=lambda x: x.place)

        return ConferenceStandings(
            sport=matching_standing.sport,
            division=matching_standing.division,
            gender=matching_standing.gender,
            year=year,
            conference=matching_standing.conference,
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
