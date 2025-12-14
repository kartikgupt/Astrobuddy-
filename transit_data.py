"""
Vedic Transit Utility (Gochar) - Lahiri Ayanamsa Fixed.

This script uses the high-precision Swiss Ephemeris (pyswisseph) 
to calculate the current position of Navagrahas using the standard 
Lahiri (Chitrapaksha) Ayanamsa. This ensures that Transit calculations 
are accurate and align with the user's verified Dasha/Chart system.

This utility is robust and dynamic, calculating transits for the current 
local date and time, thus avoiding repetitive manual calculation errors.

NOTE: Requires 'swisseph' and 'pytz' packages. Install using:
pip install pyswisseph pytz
"""
import swisseph as swe
from datetime import datetime
import pytz

# --- Configuration Constants ---
# Setting Ayanamsa to Lahiri (Chitrapaksha) for Vedic alignment
AYANAMSA_ID = swe.SIDM_LAHIRI  # Correct constant name (no SE_ prefix)
# Standard flags for SIDEREAL (Nirayana) geocentric calculations
SWEPH_FLAGS = swe.FLG_SPEED | swe.FLG_SWIEPH | swe.FLG_SIDEREAL  # Added FLG_SIDEREAL!

PLANETS = {
    'Sun': swe.SUN, 
    'Moon': swe.MOON, 
    'Mars': swe.MARS, 
    'Mercury': swe.MERCURY, 
    'Jupiter': swe.JUPITER, 
    'Venus': swe.VENUS, 
    'Saturn': swe.SATURN, 
    'Rahu': swe.TRUE_NODE, 
    'Ketu': swe.TRUE_NODE  # Ketu is 180° opposite Rahu
}

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

TIMEZONE_STR = 'Asia/Kolkata'  # IST timezone used for the user's base location

def format_longitude(longitude):
    """Converts a degree longitude into Sign, Degree, Minute, Second format."""
    
    # 1. Determine Sign
    sign_index = int(longitude // 30) % 12
    sign_name = ZODIAC_SIGNS[sign_index]
    
    # 2. Degree, Minute, Second within the sign
    degree_in_sign = longitude % 30
    deg = int(degree_in_sign)
    minutes = int((degree_in_sign - deg) * 60)
    seconds = int(((degree_in_sign - deg) * 60 - minutes) * 60)
    
    degree_str = f"{deg}°{minutes}'{seconds}\""
    return sign_name, degree_str

def calculate_current_transits(date_time_obj):
    """
    Calculates the NIRAYANA (Sidereal) positions of the Navagrahas for a given date/time 
    using the Lahiri Ayanamsa.
    
    Args:
        date_time_obj (datetime): A timezone-aware datetime object for transit time.
        
    Returns:
        list: List of dictionaries containing transit data for each planet.
    """
    
    # Set the Ayanamsa to Lahiri (CRITICAL FIX)
    swe.set_sid_mode(AYANAMSA_ID)
    
    # Convert datetime object (with timezone info) to Julian Day (JD)
    utc_datetime = date_time_obj.astimezone(pytz.utc)
    jd = swe.utc_to_jd(
        utc_datetime.year, utc_datetime.month, utc_datetime.day,
        utc_datetime.hour, utc_datetime.minute, utc_datetime.second,
        swe.GREG_CAL
    )[1]

    # Get current Ayanamsa value for debugging
    ayanamsa_value = swe.get_ayanamsa_ut(jd)
    
    print(f"\n[DEBUG] Ayanamsa (Lahiri) for JD {jd:.2f}: {ayanamsa_value:.4f}°")
    print(f"[DEBUG] Calculation Mode: SIDEREAL (Nirayana)\n")

    transit_data = []

    for name, planet_id in PLANETS.items():
        if name == 'Ketu':
            # Ketu is calculated 180 degrees opposite Rahu (True Node)
            rahu_data = swe.calc_ut(jd, swe.TRUE_NODE, SWEPH_FLAGS)
            longitude = (rahu_data[0][0] + 180) % 360 
        else:
            # Calculate planet position with SIDEREAL flag
            result = swe.calc_ut(jd, planet_id, SWEPH_FLAGS)
            longitude = result[0][0]
        
        sign, degree_str = format_longitude(longitude)
        
        transit_data.append({
            "Planet": name,
            "Sign": sign,
            "Degree_in_Sign": degree_str,
            "Longitude_Full": longitude  # Useful for LLM calculations
        })
        
    return transit_data

def display_transits(transit_results, current_time_str):
    """Prints the transit results in a readable table format."""
    
    print("\n" + "="*60)
    print(f"  GOCHAR (TRANSIT) - Current Planetary Positions")
    print(f"  Ayanamsa: Lahiri (Chitrapaksha) - Nirayana System")
    print(f"  Time: {current_time_str}")
    print("="*60)
    
    print(f"{'Planet':<15} | {'Sign':<15} | {'Degree':<15}")
    print("-" * 45)
    
    for data in transit_results:
        print(f"{data['Planet']:<15} | {data['Sign']:<15} | {data['Degree_in_Sign']:<15}")
        
    print("-" * 45)

# --- Main Execution Example ---
if __name__ == "__main__":
    # This example calculates transits for the current time (Nov 9, 2025)
    try:
        ist_tz = pytz.timezone(TIMEZONE_STR)
        
        # Use current system time OR fixed date/time for consistency:
        # Option 1: Current time
        current_time_ist = datetime.now(ist_tz)
        
        # Option 2: Fixed time for testing (uncomment to use)
        # current_time_ist = ist_tz.localize(datetime(2025, 11, 9, 16, 31, 0))
        
        current_time_str = current_time_ist.strftime("%Y-%m-%d %H:%M:%S IST")
        
        # Calculate the transits
        transits = calculate_current_transits(current_time_ist)
        
        # Display the results
        display_transits(transits, current_time_str)

        # Example of how to integrate this into your LLM data:
        print("\n" + "="*60)
        print("Transit Data (For Integration/Verification):")
        print("="*60)
        for t in transits:
            print(f"{t['Planet']:<10}: {t['Sign']:<12} {t['Degree_in_Sign']:<12} (Full Long: {t['Longitude_Full']:.4f}°)")
        
    except pytz.exceptions.UnknownTimeZoneError:
        print(f"Error: Timezone '{TIMEZONE_STR}' is unknown. Please ensure pytz is installed.")
    except Exception as e:
        print(f"An error occurred during transit calculation: {e}")
        import traceback
        traceback.print_exc()