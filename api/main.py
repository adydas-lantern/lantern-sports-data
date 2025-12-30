"""
NAIA Wrestling Standings API
FastAPI application with OpenAPI/Swagger documentation
"""
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from pathlib import Path as FilePath

from api.models import (
    School,
    Standing,
    Conference,
    ConferenceStandings,
    ScrapeRequest,
    ScrapeResult,
    HealthResponse,
    ErrorResponse,
    PaginatedResponse
)
from api.data_loader import DataLoader

# API Version
API_VERSION = "1.0.0"

# Initialize FastAPI app
app = FastAPI(
    title="NAIA Athletics Data API",
    description="""
    Multi-sport API for querying NAIA athletics conference standings and team data.

    ## Features
    * **Multi-Sport Support** - Wrestling (currently available), expandable to basketball, soccer, volleyball, etc.
    * **Multi-Division Support** - NAIA (currently available), expandable to NCAA D1/D2/D3
    * **Query Filtering** - Filter by sport, division, gender, conference, year
    * **School Data** - Query schools and their complete placement history
    * **Conference Standings** - Get conference standings by year with detailed rankings
    * **Paginated Results** - Efficient data retrieval with pagination support
    * **Full OpenAPI/Swagger Documentation** - Interactive API explorer

    ## Current Data Coverage (Wrestling)
    * **152 schools** across all NAIA wrestling conferences
    * **376 standing entries** from 2020-2025
    * Complete tournament and poll data
    * All data tagged as sport=wrestling, division=naia, gender=mens

    ## Query Parameters
    All endpoints support optional filtering:
    * `sport` - Filter by sport (wrestling, basketball, etc.)
    * `division` - Filter by division (naia, ncaa-d1, ncaa-d2, ncaa-d3)
    * `gender` - Filter by gender (mens, womens, coed)
    * `conference` - Filter by conference name (partial match)

    ## Example Queries
    * `/api/v1/schools?sport=wrestling&division=naia`
    * `/api/v1/standings/2024?sport=wrestling&gender=mens`
    * `/api/v1/conferences?division=naia`
    """,
    version=API_VERSION,
    contact={
        "name": "AthleteHub - Lantern Sports Data",
        "url": "https://api.athletehub.lanternbrp.com"
    },
    license_info={
        "name": "Educational Use",
        "url": "https://github.com/adydas-lantern/lantern-sports-data"
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data loader
# Determine CSV paths relative to project root
BASE_DIR = FilePath(__file__).parent.parent
MAIN_CSV = BASE_DIR / "NAIA_blank - NAIA_results.csv"
SORTED_CSV = BASE_DIR / "NAIA_Complete_Sorted.csv"

data_loader = DataLoader(str(MAIN_CSV), str(SORTED_CSV))


@app.on_event("startup")
async def startup_event():
    """Load data on startup"""
    print("Loading NAIA wrestling data...")
    if data_loader.load_data():
        stats = data_loader.get_stats()
        print(f"✓ Loaded {stats['total_schools']} schools, {stats['total_standings']} standings")
    else:
        print("✗ Failed to load data")


@app.get(
    "/",
    tags=["Root"],
    summary="API Information"
)
async def root():
    """Get API information and available endpoints"""
    return {
        "name": "NAIA Athletics Data API",
        "version": API_VERSION,
        "description": "Multi-sport API for NAIA athletics data",
        "current_sports": ["wrestling"],
        "supported_divisions": ["naia"],
        "supported_genders": ["mens"],
        "expandable_to": {
            "sports": ["basketball", "soccer", "volleyball", "etc"],
            "divisions": ["ncaa-d1", "ncaa-d2", "ncaa-d3"],
            "genders": ["womens", "coed"]
        },
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "health": "/health",
            "stats": "/api/v1/stats",
            "schools": "/api/v1/schools?sport=wrestling&division=naia&gender=mens",
            "conferences": "/api/v1/conferences?sport=wrestling",
            "standings": "/api/v1/standings/{year}?sport=wrestling"
        }
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health Check"
)
async def health_check():
    """Check API health and data status"""
    stats = data_loader.get_stats()

    return HealthResponse(
        status="healthy" if data_loader.loaded else "unhealthy",
        version=API_VERSION,
        data_loaded=data_loader.loaded,
        total_schools=stats.get("total_schools", 0),
        total_standings=stats.get("total_standings", 0)
    )


@app.get(
    "/api/v1/schools",
    response_model=List[School],
    tags=["Schools"],
    summary="List All Schools",
    description="Get a list of all schools with their placement history"
)
async def get_schools(
    skip: int = Query(0, ge=0, description="Number of schools to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum schools to return"),
    conference: Optional[str] = Query(None, description="Filter by conference name"),
    sport: Optional[str] = Query(None, description="Filter by sport (wrestling, basketball, etc)"),
    division: Optional[str] = Query(None, description="Filter by division (naia, ncaa-d1, ncaa-d2, ncaa-d3)"),
    gender: Optional[str] = Query(None, description="Filter by gender (mens, womens, coed)")
):
    """Get all schools with optional pagination and filtering"""
    if not data_loader.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")

    schools = data_loader.get_all_schools(sport=sport, division=division, gender=gender)

    # Filter by conference if specified
    if conference:
        conf_lower = conference.lower()
        schools = [s for s in schools if conf_lower in s.conference.lower()]

    # Pagination
    total = len(schools)
    schools = schools[skip:skip + limit]

    return schools


@app.get(
    "/api/v1/schools/{school_name}",
    response_model=School,
    tags=["Schools"],
    summary="Get School by Name",
    description="Get detailed information about a specific school",
    responses={404: {"model": ErrorResponse}}
)
async def get_school(
    school_name: str = Path(..., description="School name (case-insensitive partial match)"),
    sport: Optional[str] = Query(None, description="Filter by sport"),
    division: Optional[str] = Query(None, description="Filter by division"),
    gender: Optional[str] = Query(None, description="Filter by gender")
):
    """Get a specific school by name"""
    if not data_loader.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")

    school = data_loader.get_school_by_name(school_name, sport=sport, division=division, gender=gender)

    if not school:
        raise HTTPException(
            status_code=404,
            detail=f"School not found: {school_name}"
        )

    return school


@app.get(
    "/api/v1/conferences",
    response_model=List[Conference],
    tags=["Conferences"],
    summary="List All Conferences",
    description="Get a list of all conferences with their schools and active years"
)
async def get_conferences(
    sport: Optional[str] = Query(None, description="Filter by sport (wrestling, basketball, etc)"),
    division: Optional[str] = Query(None, description="Filter by division (naia, ncaa-d1, ncaa-d2, ncaa-d3)"),
    gender: Optional[str] = Query(None, description="Filter by gender (mens, womens, coed)")
):
    """Get all conferences with optional filtering"""
    if not data_loader.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")

    return data_loader.get_all_conferences(sport=sport, division=division, gender=gender)


@app.get(
    "/api/v1/conferences/{conference_name}",
    response_model=Conference,
    tags=["Conferences"],
    summary="Get Conference by Name",
    description="Get detailed information about a specific conference",
    responses={404: {"model": ErrorResponse}}
)
async def get_conference(
    conference_name: str = Path(..., description="Conference name (case-insensitive partial match)"),
    sport: Optional[str] = Query(None, description="Filter by sport (wrestling, basketball, etc)"),
    division: Optional[str] = Query(None, description="Filter by division (naia, ncaa-d1, ncaa-d2, ncaa-d3)"),
    gender: Optional[str] = Query(None, description="Filter by gender (mens, womens, coed)")
):
    """Get a specific conference by name with optional filtering"""
    if not data_loader.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")

    conference = data_loader.get_conference_by_name(conference_name)

    if not conference:
        raise HTTPException(
            status_code=404,
            detail=f"Conference not found: {conference_name}"
        )

    # Apply filters if specified
    if sport and conference.sport != sport:
        raise HTTPException(status_code=404, detail=f"Conference not found with sport={sport}")
    if division and conference.division != division:
        raise HTTPException(status_code=404, detail=f"Conference not found with division={division}")
    if gender and conference.gender != gender:
        raise HTTPException(status_code=404, detail=f"Conference not found with gender={gender}")

    return conference


@app.get(
    "/api/v1/conferences/{conference_name}/standings",
    response_model=dict,
    tags=["Conferences"],
    summary="Get Conference Standings",
    description="Get all standings for a conference, grouped by year",
    responses={404: {"model": ErrorResponse}}
)
async def get_conference_standings(
    conference_name: str = Path(..., description="Conference name (case-insensitive partial match)"),
    sport: Optional[str] = Query(None, description="Filter by sport (wrestling, basketball, etc)"),
    division: Optional[str] = Query(None, description="Filter by division (naia, ncaa-d1, ncaa-d2, ncaa-d3)"),
    gender: Optional[str] = Query(None, description="Filter by gender (mens, womens, coed)")
):
    """Get all standings for a conference with optional filtering"""
    if not data_loader.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")

    standings = data_loader.get_conference_standings(conference_name)

    if not standings:
        raise HTTPException(
            status_code=404,
            detail=f"Conference not found: {conference_name}"
        )

    # Filter standings if sport/division/gender specified
    if sport or division or gender:
        filtered_standings = {}
        for year, year_standings in standings.items():
            filtered = [
                s for s in year_standings
                if (not sport or s.sport == sport)
                and (not division or s.division == division)
                and (not gender or s.gender == gender)
            ]
            if filtered:
                filtered_standings[year] = filtered
        standings = filtered_standings

    return {
        "conference": conference_name,
        "years": standings
    }


@app.get(
    "/api/v1/standings/{year}",
    response_model=List[Standing],
    tags=["Standings"],
    summary="Get Standings by Year",
    description="Get all conference standings for a specific year"
)
async def get_standings_by_year(
    year: int = Path(..., ge=2020, le=2025, description="Year (2020-2025)"),
    conference: Optional[str] = Query(None, description="Filter by conference name"),
    sport: Optional[str] = Query(None, description="Filter by sport (wrestling, basketball, etc)"),
    division: Optional[str] = Query(None, description="Filter by division (naia, ncaa-d1, ncaa-d2, ncaa-d3)"),
    gender: Optional[str] = Query(None, description="Filter by gender (mens, womens, coed)")
):
    """Get all standings for a specific year with optional filtering"""
    if not data_loader.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")

    standings = data_loader.get_standings_by_year(year, sport=sport, division=division, gender=gender)

    # Filter by conference if specified
    if conference:
        conf_lower = conference.lower()
        standings = [s for s in standings if conf_lower in s.conference.lower()]

    if not standings:
        raise HTTPException(
            status_code=404,
            detail=f"No standings found for year {year}"
        )

    return standings


@app.get(
    "/api/v1/standings/{year}/{conference_name}",
    response_model=ConferenceStandings,
    tags=["Standings"],
    summary="Get Standings by Year and Conference",
    description="Get conference standings for a specific year",
    responses={404: {"model": ErrorResponse}}
)
async def get_standings_by_year_and_conference(
    year: int = Path(..., ge=2020, le=2025, description="Year (2020-2025)"),
    conference_name: str = Path(..., description="Conference name (case-insensitive partial match)"),
    sport: Optional[str] = Query(None, description="Filter by sport (wrestling, basketball, etc)"),
    division: Optional[str] = Query(None, description="Filter by division (naia, ncaa-d1, ncaa-d2, ncaa-d3)"),
    gender: Optional[str] = Query(None, description="Filter by gender (mens, womens, coed)")
):
    """Get standings for a specific year and conference with optional filtering"""
    if not data_loader.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")

    standings = data_loader.get_standings_by_year_and_conference(
        year, conference_name, sport=sport, division=division, gender=gender
    )

    if not standings:
        raise HTTPException(
            status_code=404,
            detail=f"No standings found for {conference_name} in {year}"
        )

    return standings


@app.get(
    "/api/v1/stats",
    tags=["Stats"],
    summary="Get Database Statistics",
    description="Get statistics about the database"
)
async def get_stats():
    """Get database statistics"""
    if not data_loader.loaded:
        raise HTTPException(status_code=503, detail="Data not loaded")

    stats = data_loader.get_stats()

    return {
        "total_schools": stats["total_schools"],
        "total_standings": stats["total_standings"],
        "total_conferences": stats["total_conferences"],
        "years_covered": stats["years_covered"],
        "years": [2020, 2021, 2022, 2023, 2024, 2025]
    }


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not Found", "detail": str(exc.detail)}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": "An unexpected error occurred"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
