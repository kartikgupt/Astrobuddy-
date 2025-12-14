"""
Example script showing how to use the Kundali API
"""

import requests
import json

# API Base URL
API_URL = "http://localhost:8000"

# Example 1: Using POST request with JSON body
def example_post_request():
    """Example using POST method"""
    
    payload = {
        "name": "John Doe",
        "birth_year": 1996,
        "birth_month": 7,
        "birth_day": 4,
        "birth_hour": 10,
        "birth_minute": 30,
        "birth_second": 0,
        "latitude": 27.56,
        "longitude": 80.67,
        "country": "India",
        "timezone_offset": 5.5,
        "include_transits": True,
        "transit_timezone": "Asia/Kolkata"
    }
    
    response = requests.post(f"{API_URL}/generate", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Kundali generated successfully!")
        print(f"Name: {data['name']}")
        print(f"Current MD: {data['dasha']['current_dasha']['current_mahadasha']}")
        print(f"Transits calculated at: {data['transits']['calculated_at']}")
        
        # Save to file
        with open("kundali_response.json", "w") as f:
            json.dump(data, f, indent=2)
        print("Response saved to kundali_response.json")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


# Example 2: Using GET request with query parameters
def example_get_request():
    """Example using GET method"""
    
    params = {
        "name": "Jane Smith",
        "birth_year": 1990,
        "birth_month": 5,
        "birth_day": 15,
        "birth_hour": 14,
        "birth_minute": 45,
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "include_transits": True
    }
    
    response = requests.get(f"{API_URL}/generate", params=params)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Kundali generated successfully!")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


# Example 3: Using place name for geocoding
def example_with_geocoding():
    """Example using city/country for automatic geocoding"""
    
    payload = {
        "name": "Test User",
        "birth_year": 2000,
        "birth_month": 1,
        "birth_day": 1,
        "birth_hour": 12,
        "birth_minute": 0,
        "city": "Delhi",
        "state": "Delhi",
        "country": "India",
        "include_transits": True
    }
    
    response = requests.post(f"{API_URL}/generate", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Kundali generated with geocoding!")
        print(f"Coordinates used: {data['birth_details']['latitude']}, {data['birth_details']['longitude']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("=" * 60)
    print("Kundali API Examples")
    print("=" * 60)
    
    print("\n1. Testing POST request...")
    example_post_request()
    
    print("\n2. Testing GET request...")
    # example_get_request()
    
    print("\n3. Testing with geocoding...")
    # example_with_geocoding()

