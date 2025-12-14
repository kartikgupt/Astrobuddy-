"""
Kundali API - FastAPI endpoint combining Birth Chart and Transit calculations
Combines generate_kundali.py and transit_data.py into a single API endpoint
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional
import pytz
import json

# Import from existing modules
from jyotishganit import calculate_birth_chart, get_birth_chart_json_string
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import swisseph as swe
import time

# Import constants and functions from generate_kundali.py
from generate_kundali import (
    DURATIONS, DASHAS_IN_ORDER, NAKSHATRA_LORDS, NAKSHATRA_ARC,
    AYANAMSA_CORRECTION_DEGREE, calculate_custom_dasha, 
    get_timezone_from_country, get_coordinates_from_place,
    extract_aspects_from_chart
)

# Import constants and functions from transit_data.py
from transit_data import (
    AYANAMSA_ID, SWEPH_FLAGS, PLANETS, ZODIAC_SIGNS,
    format_longitude, calculate_current_transits
)

app = FastAPI(
    title="AstroBuddy Kundali API",
    description="Vedic Astrology API for Birth Chart (Kundali) and Transit calculations",
    version="1.0.0"
)

# --- CORS Configuration ---
# Allow requests from frontend (localhost:3000, 5173, 8080)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173",
        "http://localhost:8080",  # Alternative frontend port
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# --- Request Models ---
class BirthChartRequest(BaseModel):
    """Request model for birth chart calculation"""
    name: str = Field(..., description="Name of the person")
    birth_year: int = Field(..., ge=1900, le=2100, description="Birth year")
    birth_month: int = Field(..., ge=1, le=12, description="Birth month (1-12)")
    birth_day: int = Field(..., ge=1, le=31, description="Birth day (1-31)")
    birth_hour: int = Field(..., ge=0, le=23, description="Birth hour (0-23)")
    birth_minute: int = Field(..., ge=0, le=59, description="Birth minute (0-59)")
    birth_second: int = Field(default=0, ge=0, le=59, description="Birth second (0-59)")
    
    # Location options - either provide coordinates OR place details
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude (-90 to 90)")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude (-180 to 180)")
    
    # Place name (alternative to coordinates)
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State/Province name")
    country: Optional[str] = Field(None, description="Country name")
    
    # Timezone
    timezone_offset: Optional[float] = Field(None, description="Timezone offset in hours (e.g., 5.5 for IST)")
    
    # Transit calculation
    include_transits: bool = Field(default=True, description="Include current transit data")
    transit_timezone: Optional[str] = Field(default="Asia/Kolkata", description="Timezone for transit calculation (e.g., 'Asia/Kolkata')")


# --- Helper Functions ---
def prepare_birth_data(request: BirthChartRequest):
    """Prepare birth data from request, handling geocoding if needed"""
    
    # Create birth datetime
    birth_date = datetime(
        request.birth_year,
        request.birth_month,
        request.birth_day,
        request.birth_hour,
        request.birth_minute,
        request.birth_second
    )
    
    # Handle location
    latitude = request.latitude
    longitude = request.longitude
    
    # If coordinates not provided, try geocoding
    if latitude is None or longitude is None:
        if request.city and request.country:
            try:
                latitude, longitude = get_coordinates_from_place(
                    request.city,
                    request.state or "",
                    request.country
                )
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not find coordinates for {request.city}, {request.country}. Please provide latitude and longitude directly."
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either provide latitude/longitude OR city/country for geocoding"
            )
    
    # Handle timezone
    timezone_offset = request.timezone_offset
    if timezone_offset is None:
        if request.country:
            timezone_offset = get_timezone_from_country(request.country)
        else:
            # Default to IST
            timezone_offset = 5.5
    
    return {
        'name': request.name,
        'birth_date': birth_date,
        'latitude': latitude,
        'longitude': longitude,
        'timezone_offset': timezone_offset
    }


def get_kundali_json_data(chart, name):
    """Extract kundali data as JSON (D1, D9, Aspects)"""
    # Get full JSON string and parse it
    json_string = get_birth_chart_json_string(chart)
    full_data = json.loads(json_string)
    
    # Extract only required data: D1, D9, and Aspects
    divisional_charts = full_data.get("divisionalCharts", {})
    d9_data = divisional_charts.get("d9", {}) if divisional_charts else {}
    
    filtered_data = {
        "@context": full_data.get("@context", ""),
        "@type": "VedicBirthChart",
        "d1Chart": full_data.get("d1Chart", {}),
        "d9": d9_data,
        "aspects": extract_aspects_from_chart(full_data)
    }
    
    return filtered_data


def get_current_dasha_info(custom_dasha_results):
    """Extract current running Dasha information"""
    current_md = next(
        (p for p in custom_dasha_results 
         if datetime.strptime(p['End'], "%Y-%m-%d") > datetime.now()),
        None
    )
    
    current_dasha_info = {
        "current_mahadasha": None,
        "current_antardasha": None,
        "next_mahadasha": None
    }
    
    if current_md:
        current_dasha_info["current_mahadasha"] = {
            "planet": current_md['MD'],
            "start": current_md['Start'],
            "end": current_md['End']
        }
        
        # Find current Antardasha
        current_ad = next(
            (ad for ad in current_md['AD_Cycle'] 
             if datetime.strptime(ad['End'], "%Y-%m-%d") > datetime.now()),
            None
        )
        
        if current_ad:
            current_dasha_info["current_antardasha"] = {
                "planet": current_ad['AD'],
                "start": current_ad['Start'],
                "end": current_ad['End']
            }
        
        # Find next Mahadasha
        next_md_index = custom_dasha_results.index(current_md) + 1
        if next_md_index < len(custom_dasha_results):
            next_md = custom_dasha_results[next_md_index]
            current_dasha_info["next_mahadasha"] = {
                "planet": next_md['MD'],
                "start": next_md['Start'],
                "end": next_md['End']
            }
    
    return current_dasha_info


# --- API Endpoints ---
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AstroBuddy Kundali API",
        "version": "1.0.0",
        "endpoints": {
            "/generate": "POST - Generate complete kundali with transits",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/generate")
async def generate_kundali(request: BirthChartRequest):
    """
    Generate complete Kundali (Birth Chart) with Transit data
    
    This endpoint combines:
    1. Birth Chart calculation (D1, D9, Aspects, Dasha)
    2. Current Transit positions (Gochar)
    
    Returns a combined JSON response with all data.
    """
    try:
        # 1. Prepare birth data
        user_data = prepare_birth_data(request)
        
        # 2. Calculate birth chart
        chart = calculate_birth_chart(
            birth_date=user_data['birth_date'],
            latitude=user_data['latitude'],
            longitude=user_data['longitude'],
            timezone_offset=user_data['timezone_offset'],
            name=user_data['name']
        )
        
        # 3. Calculate custom Dasha
        custom_dasha_results = calculate_custom_dasha(
            user_data['birth_date'],
            chart
        )
        
        # 4. Get Kundali JSON data (D1, D9, Aspects)
        kundali_data = get_kundali_json_data(chart, user_data['name'])
        
        # 5. Get current Dasha info
        dasha_info = get_current_dasha_info(custom_dasha_results)
        
        # 6. Calculate transits if requested
        transit_data = None
        transit_time = None
        if request.include_transits:
            try:
                # Get timezone for transit calculation
                transit_tz = pytz.timezone(request.transit_timezone)
                current_time = datetime.now(transit_tz)
                transit_time = current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
                
                # Calculate transits
                transit_data = calculate_current_transits(current_time)
            except Exception as e:
                # If transit calculation fails, continue without it
                transit_data = None
                transit_time = None
        
        # 7. Combine all data into single response
        response_data = {
            "name": user_data['name'],
            "birth_details": {
                "birth_date": user_data['birth_date'].isoformat(),
                "latitude": user_data['latitude'],
                "longitude": user_data['longitude'],
                "timezone_offset": user_data['timezone_offset']
            },
            "kundali": kundali_data,
            "dasha": {
                "vimshottari_dasha": custom_dasha_results,
                "current_dasha": dasha_info
            },
            "transits": {
                "calculated_at": transit_time,
                "planets": transit_data
            } if transit_data else None
        }
        
        return JSONResponse(content=response_data)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating Kundali: {str(e)}"
        )


# --- Alternative GET endpoint for simple queries ---
@app.get("/generate")
async def generate_kundali_get(
    name: str = Query(..., description="Name of the person"),
    birth_year: int = Query(..., ge=1900, le=2100),
    birth_month: int = Query(..., ge=1, le=12),
    birth_day: int = Query(..., ge=1, le=31),
    birth_hour: int = Query(..., ge=0, le=23),
    birth_minute: int = Query(..., ge=0, le=59),
    birth_second: int = Query(default=0, ge=0, le=59),
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    timezone_offset: Optional[float] = Query(None),
    include_transits: bool = Query(default=True),
    transit_timezone: str = Query(default="Asia/Kolkata")
):
    """GET endpoint for generating kundali (alternative to POST)"""
    request = BirthChartRequest(
        name=name,
        birth_year=birth_year,
        birth_month=birth_month,
        birth_day=birth_day,
        birth_hour=birth_hour,
        birth_minute=birth_minute,
        birth_second=birth_second,
        latitude=latitude,
        longitude=longitude,
        city=city,
        state=state,
        country=country,
        timezone_offset=timezone_offset,
        include_transits=include_transits,
        transit_timezone=transit_timezone
    )
    return await generate_kundali(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

