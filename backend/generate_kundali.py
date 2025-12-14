"""
Kundali Generator Script - WITH DYNAMIC AYANAMSA CORRECTION
Takes user input and generates a complete Vedic astrology birth chart (Kundali)
Includes corrected Vimshottari Dasha calculation aligned with Lahiri Ayanamsa
"""

from datetime import datetime, timedelta
from jyotishganit import calculate_birth_chart, get_birth_chart_json_string
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import json
import os
import time

# --- DYNAMIC DASHAA CONSTANTS ---
# Dasha periods (in years) - Fixed Vimshottari Order
DURATIONS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, 
    "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}
DASHAS_IN_ORDER = list(DURATIONS.keys())

# Nakshatra sequence and their lords for calculating Dasha balance at birth.
NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", 
    "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars", 
    "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", 
    "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]
# Each Nakshatra is 13 degrees 20 minutes (800 minutes of arc).
NAKSHATRA_ARC = 13 + 20/60 # 13.333333 degrees

# *** ADJUSTABLE AYANAMSA CORRECTION FACTOR ***
# This correction compensates for the discrepancy between
# jyotishganit's internal Ayanamsa and the standard Lahiri/Chitrapaksha Ayanamsa
# 
# TUNING GUIDE:
# - Each 1.0° correction ≈ shifts Dasha dates by ~10-11 months
# - Each 0.1° correction ≈ shifts Dasha dates by ~1 month (30-35 days)
# - If MD/AD dates are TOO LATE: INCREASE this value
# - If MD/AD dates are TOO EARLY: DECREASE this value
#
# CURRENT TESTING VALUES:
# - 0.0°  = No correction (original jyotishganit output)
# - 1.09° = Small correction (~11 months shift)
# - 2.0°  = Medium correction (~20 months shift)
# - 3.0°  = Large correction (~30 months shift)
#
# ⚙️ ADJUST THIS VALUE TO MATCH YOUR EXPECTED DASHA DATES ⚙️
AYANAMSA_CORRECTION_DEGREE = -0.8  # <-- CHANGE THIS VALUE FOR TESTING

# -------------------------------------------------------------

def calculate_custom_dasha(birth_time, chart):
    """
    Dynamically calculates the precise Vimshottari Dasha periods based on 
    the Moon's longitude with Ayanamsa correction applied.
    
    Args:
        birth_time (datetime): The time of birth.
        chart: The output object from jyotishganit containing planetary longitudes.
        
    Returns:
        list: A list of calculated Dasha periods (MD, AD, PD).
    """
    
    # 1. Get Moon's Nirayana Longitude (Graha Sphuta)
    moon_planet_data = next((p for p in chart.d1_chart.planets if p.celestial_body == "Moon"), None)
    
    if not moon_planet_data:
        print("Error: Moon data not found in chart.")
        return []

    # Moon's Longitude in the entire Zodiac (0 to 360 degrees)
    sign_to_degree = {
        'Aries': 0, 'Taurus': 30, 'Gemini': 60, 'Cancer': 90,
        'Leo': 120, 'Virgo': 150, 'Libra': 180, 'Scorpio': 210,
        'Sagittarius': 240, 'Capricorn': 270, 'Aquarius': 300, 'Pisces': 330
    }
    sign_start = sign_to_degree.get(moon_planet_data.sign, 0)
    moon_longitude_raw = sign_start + float(moon_planet_data.sign_degrees)
    
    # *** APPLY AYANAMSA CORRECTION ***
    # Subtract the correction factor to align with Lahiri Ayanamsa
    moon_longitude = moon_longitude_raw - AYANAMSA_CORRECTION_DEGREE
    
    # Handle negative longitude (wrap around the zodiac)
    if moon_longitude < 0:
        moon_longitude += 360
    
    # 2. Identify Nakshatra and Balance Dasha
    # Find the Nakshatra Index (0 to 26)
    nakshatra_index = int(moon_longitude / NAKSHATRA_ARC)
    
    # Starting Lord of the Mahadasha (MD Lord at Birth)
    md_lord_at_birth = NAKSHATRA_LORDS[nakshatra_index]
    md_duration_at_birth = DURATIONS[md_lord_at_birth]
    
    # Arc degrees traveled within the current Nakshatra
    nakshatra_start_longitude = nakshatra_index * NAKSHATRA_ARC
    arc_traveled = moon_longitude - nakshatra_start_longitude
    
    # Balance of the arc remaining (for Dasha balance)
    balance_arc = NAKSHATRA_ARC - arc_traveled
    
    # Balance Dasha in Years (Vimshottari Formula)
    balance_dasha_years = (balance_arc / NAKSHATRA_ARC) * md_duration_at_birth
    
    print(f"\n{'='*60}")
    print(f"[AYANAMSA CORRECTION DIAGNOSTICS]")
    print(f"{'='*60}")
    print(f"Correction Factor Used: {AYANAMSA_CORRECTION_DEGREE}°")
    print(f"Moon Longitude (Raw):   {moon_longitude_raw:.4f}°")
    print(f"Moon Longitude (Corrected): {moon_longitude:.4f}°")
    print(f"Nakshatra Index: {nakshatra_index} ({NAKSHATRA_LORDS[nakshatra_index]})")
    print(f"MD Lord at Birth: {md_lord_at_birth}")
    print(f"Balance Dasha: {balance_dasha_years:.4f} years")
    print(f"{'='*60}\n")
    
    # Calculate initial MD end date from birth time
    birth_date_obj = birth_time
    md_end_at_birth = birth_date_obj + timedelta(days=balance_dasha_years * 365.25)
    
    # 3. Generate Full Dasha Cycle
    
    all_dasha_results = []
    current_md_start = birth_date_obj
    current_md_end = md_end_at_birth
    
    # Find the starting index for the full 120-year cycle
    start_index = DASHAS_IN_ORDER.index(md_lord_at_birth)
    
    for i in range(9):
        md_planet = DASHAS_IN_ORDER[(start_index + i) % 9]
        md_duration_yrs = DURATIONS[md_planet]

        # Use balance Dasha for the very first period, then use full duration
        if i > 0:
            md_start = current_md_end
            md_end = md_start + timedelta(days=md_duration_yrs * 365.25)
        else:
            md_start = current_md_start
            md_end = current_md_end

        # --- Calculate Antardashas (AD) within this MD ---
        ad_results = []
        current_ad_start = md_start
        md_duration_days = (md_end - md_start).days
        
        md_ad_index = DASHAS_IN_ORDER.index(md_planet)

        for j in range(9):
            ad_planet = DASHAS_IN_ORDER[(md_ad_index + j) % 9]
            ad_duration_yrs = DURATIONS[ad_planet]
            
            # AD Duration in Days = (AD Duration / 120 Total Years) * MD Duration (in days)
            duration_days = (ad_duration_yrs / 120) * md_duration_days
            ad_end = current_ad_start + timedelta(days=duration_days)
            
            # Store AD result
            ad_results.append({
                "AD": ad_planet,
                "Start": current_ad_start.strftime("%Y-%m-%d"),
                "End": ad_end.strftime("%Y-%m-%d")
            })
            current_ad_start = ad_end

        
        # Store MD result with its complete AD cycle
        all_dasha_results.append({
            "MD": md_planet,
            "Start": md_start.strftime("%Y-%m-%d"),
            "End": md_end.strftime("%Y-%m-%d"),
            "AD_Cycle": ad_results
        })

        # Set the start of the next Mahadasha
        current_md_end = md_end
        
        # Stop after running MDs that are relevant to current time
        if md_end > datetime.now() and i > 4: 
             break
             
    return all_dasha_results

# --- UTILITY FUNCTIONS ---
def get_timezone_from_country(country):
    """Get timezone offset based on country name"""
    # Common country to timezone mapping
    country_timezone_map = {
        # India and South Asia
        'india': 5.5,
        'pakistan': 5.0,
        'bangladesh': 6.0,
        'sri lanka': 5.5,
        'nepal': 5.75,
        'bhutan': 6.0,
        
        # Middle East
        'uae': 4.0,
        'united arab emirates': 4.0,
        'saudi arabia': 3.0,
        'kuwait': 3.0,
        'qatar': 3.0,
        'bahrain': 3.0,
        'oman': 4.0,
        'israel': 2.0,
        'turkey': 3.0,
        
        # Europe
        'united kingdom': 0.0,
        'uk': 0.0,
        'germany': 1.0,
        'france': 1.0,
        'italy': 1.0,
        'spain': 1.0,
        'netherlands': 1.0,
        'belgium': 1.0,
        'switzerland': 1.0,
        'austria': 1.0,
        'portugal': 0.0,
        'greece': 2.0,
        'russia': 3.0,  # Moscow time
        
        # North America
        'usa': -5.0,  # EST (will vary by state)
        'united states': -5.0,
        'canada': -5.0,  # EST (will vary by province)
        'mexico': -6.0,
        
        # South America
        'brazil': -3.0,
        'argentina': -3.0,
        'chile': -3.0,
        
        # Asia Pacific
        'china': 8.0,
        'japan': 9.0,
        'south korea': 9.0,
        'singapore': 8.0,
        'malaysia': 8.0,
        'thailand': 7.0,
        'indonesia': 7.0,  # Western Indonesia
        'philippines': 8.0,
        'vietnam': 7.0,
        'hong kong': 8.0,
        'taiwan': 8.0,
        'australia': 10.0,  # Eastern Australia
        
        # Africa
        'south africa': 2.0,
        'egypt': 2.0,
        'kenya': 3.0,
        'nigeria': 1.0,
    }
    
    # Normalize country name (lowercase, strip spaces)
    country_normalized = country.lower().strip()
    
    # Check exact match first
    if country_normalized in country_timezone_map:
        return country_timezone_map[country_normalized]
    
    # Check partial match (in case of variations)
    for key, tz in country_timezone_map.items():
        if key in country_normalized or country_normalized in key:
            return tz
    
    # Default to IST if not found (most common for Vedic astrology users)
    return 5.5


def get_coordinates_from_place(city, state, country):
    """Get latitude and longitude from place name using geocoding"""
    geolocator = Nominatim(user_agent="astrobuddy_kundali_generator")
    
    place_queries = [
        f"{city}, {state}, {country}",
        f"{city}, {country}",
        f"{state}, {country}",
        f"{country}"
    ]
    
    location = None
    for query in place_queries:
        try:
            time.sleep(1)  # Rate limiting for Nominatim
            location = geolocator.geocode(query, timeout=10)
            if location:
                break
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"  Warning: Geocoding service error, trying next option...")
            continue
        except Exception as e:
            continue
    
    if not location:
        raise ValueError(f"Could not find coordinates for {city}, {state}, {country}. Please try entering coordinates manually.")
    
    return location.latitude, location.longitude


def get_user_input():
    """Collect birth details from user"""
    print("\n" + "="*60)
    print("  ASTROBUDDY - Kundali Generator")
    print("  Welcome to Vedic Birth Chart Calculator")
    print("="*60 + "\n")
    
    name = input("Enter your name: ").strip()
    if not name:
        name = "User"
    
    print("\nEnter birth date:")
    year = int(input("  Year (e.g., 1996): "))
    month = int(input("  Month (1-12): "))
    day = int(input("  Day (1-31): "))
    
    print("\nEnter birth time:")
    print("  Format: HH:MM or HH:MM:SS (e.g., 10:30 or 09:15:30)")
    time_input = input("  Birth time: ").strip()
    
    time_parts = time_input.split(':')
    if len(time_parts) < 2:
        raise ValueError("Time must be in HH:MM or HH:MM:SS format")
    
    hour = int(time_parts[0])
    minute = int(time_parts[1])
    
    if len(time_parts) >= 3:
        second = int(time_parts[2])
    else:
        second = 0
    
    if not (0 <= hour <= 23):
        raise ValueError("Hour must be between 0 and 23")
    if not (0 <= minute <= 59):
        raise ValueError("Minute must be between 0 and 59")
    if not (0 <= second <= 59):
        raise ValueError("Second must be between 0 and 59")
    
    print("\nEnter birth place:")
    print("  Option 1: Enter place name (City, State, Country)")
    print("  Option 2: Enter coordinates directly (Press Enter to skip place name)")
    
    city = input("  City (e.g., Sitapur): ").strip()
    country = ""
    timezone_offset = None
    
    if not city:
        print("\n  Entering coordinates manually:")
        latitude = float(input("  Latitude (e.g., 27.56): "))
        longitude = float(input("  Longitude (e.g., 80.67): "))
        # For manual coordinates, ask for country to determine timezone
        country = input("  Country (for timezone, e.g., India): ").strip()
        if country:
            timezone_offset = get_timezone_from_country(country)
            print(f"  ✓ Timezone automatically set to {timezone_offset} hours based on country: {country}")
    else:
        state = input("  State (e.g., Uttar Pradesh): ").strip()
        country = input("  Country (e.g., India): ").strip()
        
        if not state:
            state = ""
        if not country:
            country = "India"
        
        # Automatically get timezone from country
        timezone_offset = get_timezone_from_country(country)
        print(f"  ✓ Timezone automatically set to {timezone_offset} hours based on country: {country}")
        
        print(f"\n  Searching for coordinates of {city}, {state}, {country}...")
        try:
            latitude, longitude = get_coordinates_from_place(city, state, country)
            print(f"  ✓ Coordinates found: Latitude {latitude:.4f}, Longitude {longitude:.4f}")
        except ValueError as e:
            print(f"  ✗ {e}")
            print("\n  Please enter coordinates manually:")
            latitude = float(input("  Latitude (e.g., 27.56): "))
            longitude = float(input("  Longitude (e.g., 80.67): "))
    
    # If timezone not set yet, ask user
    if timezone_offset is None:
        print("\nEnter timezone offset:")
        print("  Example: 5.5 for IST, -5 for EST, 0 for GMT")
        timezone_offset = float(input("  Timezone offset: "))
    else:
        # Allow user to override if needed
        override = input(f"\n  Use timezone {timezone_offset} hours? (Press Enter to confirm, or type new value to override): ").strip()
        if override:
            try:
                timezone_offset = float(override)
                print(f"  ✓ Timezone set to {timezone_offset} hours (manual override)")
            except ValueError:
                print(f"  ✓ Using automatically detected timezone: {timezone_offset} hours")
    
    birth_date = datetime(year, month, day, hour, minute, second)
    
    return {
        'name': name,
        'birth_date': birth_date,
        'latitude': latitude,
        'longitude': longitude,
        'timezone_offset': timezone_offset
    }


def display_kundali(chart, name, custom_dasha_results):
    """Display the complete kundali information, including custom Dasha"""
    print("\n" + "="*60)
    print(f"  KUNDALI (Birth Chart for {name.upper()})")
    print("="*60)
    
    # Panchanga Details
    print("\n" + "-"*60)
    print("PANCHANGA (Five Limbs of Time)")
    print("-"*60)
    panchanga = chart.panchanga
    print(f"Tithi (Lunar Day):     {panchanga.tithi}")
    print(f"Nakshatra (Lunar Mansion): {panchanga.nakshatra}")
    print(f"Yoga (Luni-Solar Day): {panchanga.yoga}")
    print(f"Karana (Half Tithi):   {panchanga.karana}")
    print(f"Vaara (Weekday):       {panchanga.vaara}")
    
    # Lagna Details
    print("\n" + "-"*60)
    print("LAGNA (Ascendant)")
    print("-"*60)
    d1 = chart.d1_chart
    ascendant_sign = d1.houses[0].sign
    ascendant_degree = float(d1.houses[0].sign_degrees)
    
    deg = int(ascendant_degree)
    minutes = int((ascendant_degree - deg) * 60)
    seconds = int(((ascendant_degree - deg) * 60 - minutes) * 60)
    degree_str = f"{deg}°{minutes}'{seconds}\""
    print(f"Ascendant Sign:   {ascendant_sign}")
    print(f"Ascendant Degree: {degree_str}")
    
    # Planets in D1 Chart
    print("\n" + "-"*60)
    print("PLANETARY POSITIONS (D1 - Main Birth Chart)")
    print("-"*60)
    planet_names = [
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", 
        "Venus", "Saturn", "Rahu", "Ketu"
    ]
    
    print(f"{'Planet':<10} | {'Sign':<12} | {'Degree':<10} | {'House':<6}")
    print("-" * 60)
    for i, planet in enumerate(d1.planets):
        if i < len(planet_names):
            planet_name = planet_names[i]
            sign = planet.sign
            degree = float(planet.sign_degrees)
            house = planet.house
            
            deg = int(degree)
            minutes = int((degree - deg) * 60)
            seconds = int(((degree - deg) * 60 - minutes) * 60)
            degree_str = f"{deg}°{minutes}'{seconds}\""
            print(f"{planet_name:<10} | {sign:<12} | {degree_str:<10} | {house:<6}")
    
    # --- CORRECTED DASHAA OUTPUT ---
    print("\n" + "-"*60)
    print("✅ VIMSHOTTARI DASHA (Lahiri Ayanamsa Corrected)")
    print("  (Based on Moon's Degree with Ayanamsa Correction)")
    print("-"*60)

    # 1. Identify Current Running Dasha
    current_md = next((p for p in custom_dasha_results if datetime.strptime(p['End'], "%Y-%m-%d") > datetime.now()), None)
    
    if current_md:
        
        # Determine running Antardasha (AD)
        current_ad = next((ad for ad in current_md['AD_Cycle'] if datetime.strptime(ad['End'], "%Y-%m-%d") > datetime.now()), None)
        
        # Display Running Dasha
        print(f"➡️  **CURRENT MAHADASHA (MD):** {current_md['MD']}")
        print(f"    Start: {current_md['Start']} | End: {current_md['End']}")
        print("-" * 30)

        if current_ad:
            print(f"➡️  **CURRENT ANTARDASHA (AD):** {current_ad['AD']}")
            print(f"    Start: {current_ad['Start']} | End: {current_ad['End']}")
            
    # 2. Display Next Major Dasha
    next_md_index = custom_dasha_results.index(current_md) + 1 if current_md else 0
    if next_md_index < len(custom_dasha_results):
        next_md = custom_dasha_results[next_md_index]
        print("\n" + "-"*60)
        print("⭐️ NEXT MAHADASHA (MD) ⭐️")
        print(f"   {next_md['MD']} MD Start: {next_md['Start']}")
        print(f"   {next_md['MD']} MD End:   {next_md['End']}")
        print("-" * 60)


def extract_aspects_from_chart(chart_data):
    """Extract all aspect data from D1 chart"""
    aspects_data = {
        "house_aspects_received": [],
        "planetary_aspects_gives": [],
        "planetary_aspects_receives": []
    }
    
    d1_chart = chart_data.get('d1Chart', {})
    
    # Extract aspects from D1 chart houses
    if 'houses' in d1_chart:
        for house in d1_chart['houses']:
            house_num = house.get('number')
            
            # Aspects received by houses
            if 'aspectsReceived' in house and house['aspectsReceived']:
                for aspect in house['aspectsReceived']:
                    aspects_data['house_aspects_received'].append({
                        "house": house_num,
                        "aspecting_planet": aspect.get('aspecting_planet', ''),
                        "aspect_type": aspect.get('aspect_type', '')
                    })
            
            # Aspects from planets (occupants) in houses
            if 'occupants' in house:
                for occupant in house['occupants']:
                    if 'aspects' in occupant:
                        aspects = occupant.get('aspects', {})
                        planet_name = occupant.get('celestialBody', '')
                        
                        # Aspects given by planet
                        if 'gives' in aspects and aspects['gives']:
                            for aspect in aspects['gives']:
                                aspect_entry = {
                                    "from_planet": planet_name,
                                    "aspect_type": aspect.get('aspect_type', '')
                                }
                                if 'to_planet' in aspect:
                                    aspect_entry['to_planet'] = aspect.get('to_planet')
                                if 'to_house' in aspect:
                                    aspect_entry['to_house'] = aspect.get('to_house')
                                aspects_data['planetary_aspects_gives'].append(aspect_entry)
                        
                        # Aspects received by planet
                        if 'receives' in aspects and aspects['receives']:
                            for aspect in aspects['receives']:
                                aspect_entry = {
                                    "to_planet": planet_name,
                                    "aspect_type": aspect.get('aspect_type', '')
                                }
                                if 'from_planet' in aspect:
                                    aspect_entry['from_planet'] = aspect.get('from_planet')
                                aspects_data['planetary_aspects_receives'].append(aspect_entry)
    
    return aspects_data


def save_kundali_json(chart, name):
    """Save kundali to JSON file with only D1, D9, and Aspect data"""
    output_dir = "kundali_outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_')
    filename = f"{safe_name}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Get full JSON string and parse it
    json_string = get_birth_chart_json_string(chart)
    full_data = json.loads(json_string)
    
    # Extract only required data: D1, D9, and Aspects
    # D9 is inside divisionalCharts
    divisional_charts = full_data.get("divisionalCharts", {})
    d9_data = divisional_charts.get("d9", {}) if divisional_charts else {}
    
    filtered_data = {
        "@context": full_data.get("@context", ""),
        "@type": "VedicBirthChart",
        "d1Chart": full_data.get("d1Chart", {}),
        "d9": d9_data,
        "aspects": extract_aspects_from_chart(full_data)
    }
    
    # Save filtered JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=2, default=str)
    
    print(f"✓ Kundali saved to JSON file (D1, D9, and Aspects only): {filepath}")
    return filepath


def main():
    """Main function to generate kundali"""
    try:
        user_data = get_user_input()
        
        print("\n" + "-"*60)
        print("Calculating your Kundali...")
        print("-"*60)
        
        # 1. Calculate the core birth chart
        chart = calculate_birth_chart(
            birth_date=user_data['birth_date'],
            latitude=user_data['latitude'],
            longitude=user_data['longitude'],
            timezone_offset=user_data['timezone_offset'],
            name=user_data['name']
        )
        
        # 2. Calculate the CORRECTED Dasha timings
        custom_dasha_results = calculate_custom_dasha(user_data['birth_date'], chart)
        
        # 3. Display kundali
        display_kundali(chart, user_data['name'], custom_dasha_results)
        
        # 4. Save to JSON
        json_path = save_kundali_json(chart, user_data['name'])
        
        print(f"\n✓ Complete Kundali data has been saved to JSON file.\n")
        
    except ValueError as e:
        print(f"\n✗ Error: Invalid input - {e}")
        print("Please check your input values and try again.\n")
    except Exception as e:
        print(f"\n✗ Error generating Kundali: {e}")
        print("Please ensure all inputs are correct and try again.\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()