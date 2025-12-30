"""
Pydantic models for NAIA Wrestling API
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class SchoolPlacement(BaseModel):
    """Single year placement for a school"""
    year: int = Field(..., description="Year of placement (2020-2025)")
    place: int = Field(..., description="Conference placement (1-10+)")
    conference: str = Field(..., description="Conference name")


class School(BaseModel):
    """School entity with all placements"""
    name: str = Field(..., description="School name")
    division: str = Field(default="NAIA", description="College division")
    conference: str = Field(..., description="Primary conference")
    placements: List[SchoolPlacement] = Field(default=[], description="All year placements")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Grand View (Iowa) - Mens",
                "division": "NAIA",
                "conference": "Heart of America Athletic Conference",
                "placements": [
                    {"year": 2020, "place": 1, "conference": "Heart of America Athletic Conference"},
                    {"year": 2021, "place": 1, "conference": "Heart of America Athletic Conference"}
                ]
            }
        }


class Standing(BaseModel):
    """Single standing entry"""
    year: int = Field(..., description="Year")
    conference: str = Field(..., description="Conference name")
    place: int = Field(..., description="Placement")
    school: str = Field(..., description="School name")

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2020,
                "conference": "Heart of America Athletic Conference",
                "place": 1,
                "school": "Grand View (Iowa) - Mens"
            }
        }


class Conference(BaseModel):
    """Conference entity"""
    name: str = Field(..., description="Conference name")
    schools: List[str] = Field(default=[], description="Schools in conference")
    years_active: List[int] = Field(default=[], description="Years with data")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Heart of America Athletic Conference",
                "schools": ["Grand View (Iowa) - Mens", "Missouri Valley College"],
                "years_active": [2020, 2021, 2022, 2023, 2024, 2025]
            }
        }


class ConferenceStandings(BaseModel):
    """Conference standings for a specific year"""
    year: int = Field(..., description="Year")
    conference: str = Field(..., description="Conference name")
    standings: List[Standing] = Field(..., description="Ordered standings")

    class Config:
        json_schema_extra = {
            "example": {
                "year": 2020,
                "conference": "Heart of America Athletic Conference",
                "standings": [
                    {"year": 2020, "conference": "Heart of America Athletic Conference", "place": 1, "school": "Grand View (Iowa) - Mens"},
                    {"year": 2020, "conference": "Heart of America Athletic Conference", "place": 2, "school": "Missouri Valley College"}
                ]
            }
        }


class ScrapeRequest(BaseModel):
    """Request to scrape a URL"""
    url: str = Field(..., description="NAIA standings URL to scrape")
    year: int = Field(..., ge=2020, le=2030, description="Year to scrape for")
    force: bool = Field(default=False, description="Force re-scrape if URL already processed")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://www.naia.org/sports/mwrest/2025-26/Releases/Conf_3",
                "year": 2025,
                "force": False
            }
        }


class ScrapeResult(BaseModel):
    """Result of scraping operation"""
    success: bool = Field(..., description="Whether scraping succeeded")
    url: str = Field(..., description="URL that was scraped")
    year: int = Field(..., description="Year scraped for")
    schools_updated: int = Field(default=0, description="Number of schools updated")
    schools_added: int = Field(default=0, description="Number of schools added")
    conferences_found: int = Field(default=0, description="Number of conferences found")
    message: str = Field(default="", description="Status message")
    errors: List[str] = Field(default=[], description="Any errors encountered")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "url": "https://www.naia.org/sports/mwrest/2025-26/Releases/Conf_3",
                "year": 2025,
                "schools_updated": 58,
                "schools_added": 2,
                "conferences_found": 8,
                "message": "Successfully scraped 60 standings from 8 conferences",
                "errors": []
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    data_loaded: bool = Field(..., description="Whether data is loaded")
    total_schools: int = Field(default=0, description="Total schools in database")
    total_standings: int = Field(default=0, description="Total standing entries")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "data_loaded": True,
                "total_schools": 152,
                "total_standings": 376
            }
        }


class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "School not found",
                "detail": "No school found with name 'Invalid School'"
            }
        }


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    total: int = Field(..., description="Total items")
    page: int = Field(..., description="Current page (1-indexed)")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total pages")
    items: List[dict] = Field(..., description="Items for current page")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 152,
                "page": 1,
                "page_size": 50,
                "total_pages": 4,
                "items": []
            }
        }
