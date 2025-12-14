# Kundali API Documentation

यह API `generate_kundali.py` और `transit_data.py` को combine करके एक single endpoint बनाती है जो complete Kundali data और Transit data को एक साथ return करती है।

## Installation

```bash
pip install -r requirements.txt
```

## Running the API

```bash
python kundali_api.py
```

या uvicorn से directly:

```bash
uvicorn kundali_api:app --host 0.0.0.0 --port 8000 --reload
```

API `http://localhost:8000` पर चलेगी।

## API Endpoints

### 1. Root Endpoint
```
GET /
```
API information return करता है।

### 2. Health Check
```
GET /health
```
API health check करता है।

### 3. Generate Kundali (POST)
```
POST /generate
```

**Request Body (JSON):**
```json
{
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
  "include_transits": true,
  "transit_timezone": "Asia/Kolkata"
}
```

**Parameters:**
- `name` (required): व्यक्ति का नाम
- `birth_year` (required): जन्म वर्ष (1900-2100)
- `birth_month` (required): जन्म महीना (1-12)
- `birth_day` (required): जन्म दिन (1-31)
- `birth_hour` (required): जन्म घंटा (0-23)
- `birth_minute` (required): जन्म मिनट (0-59)
- `birth_second` (optional, default=0): जन्म सेकंड (0-59)
- `latitude` (optional): अक्षांश (-90 to 90)
- `longitude` (optional): देशांतर (-180 to 180)
- `city` (optional): शहर का नाम (geocoding के लिए)
- `state` (optional): राज्य/प्रांत का नाम
- `country` (optional): देश का नाम (timezone और geocoding के लिए)
- `timezone_offset` (optional): Timezone offset (hours में, e.g., 5.5 for IST)
- `include_transits` (optional, default=true): Transit data include करना है या नहीं
- `transit_timezone` (optional, default="Asia/Kolkata"): Transit calculation के लिए timezone

**Note:** या तो `latitude`/`longitude` provide करें, या `city`/`country` (geocoding के लिए)।

### 4. Generate Kundali (GET)
```
GET /generate?name=John&birth_year=1996&birth_month=7&...
```

GET method में सभी parameters query parameters के रूप में pass करें।

## Response Format

```json
{
  "name": "John Doe",
  "birth_details": {
    "birth_date": "1996-07-04T10:30:00",
    "latitude": 27.56,
    "longitude": 80.67,
    "timezone_offset": 5.5
  },
  "kundali": {
    "@context": "...",
    "@type": "VedicBirthChart",
    "d1Chart": { ... },
    "d9": { ... },
    "aspects": { ... }
  },
  "dasha": {
    "vimshottari_dasha": [
      {
        "MD": "Venus",
        "Start": "1996-07-04",
        "End": "2016-07-04",
        "AD_Cycle": [ ... ]
      },
      ...
    ],
    "current_dasha": {
      "current_mahadasha": {
        "planet": "Venus",
        "start": "1996-07-04",
        "end": "2016-07-04"
      },
      "current_antardasha": {
        "planet": "Sun",
        "start": "2024-01-01",
        "end": "2024-07-01"
      },
      "next_mahadasha": {
        "planet": "Sun",
        "start": "2016-07-04",
        "end": "2022-07-04"
      }
    }
  },
  "transits": {
    "calculated_at": "2024-01-15 14:30:00 IST",
    "planets": [
      {
        "Planet": "Sun",
        "Sign": "Capricorn",
        "Degree_in_Sign": "0°15'30\"",
        "Longitude_Full": 270.2583
      },
      ...
    ]
  }
}
```

## Example Usage

### Python (requests library)
```python
import requests

payload = {
    "name": "John Doe",
    "birth_year": 1996,
    "birth_month": 7,
    "birth_day": 4,
    "birth_hour": 10,
    "birth_minute": 30,
    "latitude": 27.56,
    "longitude": 80.67,
    "country": "India",
    "include_transits": True
}

response = requests.post("http://localhost:8000/generate", json=payload)
data = response.json()
print(data)
```

### cURL
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "birth_year": 1996,
    "birth_month": 7,
    "birth_day": 4,
    "birth_hour": 10,
    "birth_minute": 30,
    "latitude": 27.56,
    "longitude": 80.67,
    "country": "India"
  }'
```

### Using Geocoding (City/Country)
```python
payload = {
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

response = requests.post("http://localhost:8000/generate", json=payload)
```

## API Documentation (Swagger UI)

API start करने के बाद, interactive documentation यहाँ available है:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

API standard HTTP status codes return करती है:
- `200`: Success
- `400`: Bad Request (invalid input)
- `500`: Internal Server Error

Error response format:
```json
{
  "detail": "Error message here"
}
```

## Notes

1. **Geocoding**: अगर `latitude`/`longitude` provide नहीं किए गए हैं, तो `city` और `country` से automatically coordinates fetch होते हैं (Nominatim service use करके)।

2. **Timezone**: अगर `timezone_offset` provide नहीं किया गया है, तो `country` से automatically detect होता है।

3. **Transits**: `include_transits=false` set करके transit calculation skip कर सकते हैं।

4. **Ayanamsa Correction**: API में `generate_kundali.py` का `AYANAMSA_CORRECTION_DEGREE` factor automatically apply होता है।

## Testing

`api_example.py` file में example code है जो API को test करने के लिए use कर सकते हैं:

```bash
python api_example.py
```

