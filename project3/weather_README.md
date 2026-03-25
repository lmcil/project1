# 10-Day Weather Forecast

A console application that prompts for a US city and state, then
retrieves and displays a 10-day weather forecast using two free,
no-API-key-required endpoints from Open-Meteo.

---

## How It Works

```
User Input (city + state)
        │
        ▼
Open-Meteo Geocoding API   →  latitude, longitude
        │
        ▼
Open-Meteo Forecast API    →  10-day daily data
        │
        ▼
Formatted table in the terminal
```

The app uses the **Geocoding API** first to convert the city/state
text into GPS coordinates, filtering results to the United States and
the correct state — so "Birmingham, Alabama" won't match
"Birmingham, England".

---

## Setup

### 1 — Install Python 3.8+
Download from https://www.python.org if needed.

### 2 — Install the dependency
Open a terminal in this project folder and run:
```
pip install requests
```
Or use the requirements file:
```
pip install -r requirements.txt
```

### 3 — Run the app
```
python weather_forecast.py
```

---

## Sample Output

```
=== 10-Day Weather Forecast ===

Enter city:  Lynchburg
Enter state: Virginia

Looking up 'Lynchburg, Virginia'...
Fetching 10-day forecast for Lynchburg, Virginia...

--- 10-Day Forecast for Lynchburg, Virginia ---
Date         | Max Temp | Min Temp |       Rain
--------------------------------------------------
2026-03-23   |   57.2°F |   29.5°F |   0.000inch
2026-03-24   |   61.1°F |   38.5°F |   0.000inch
2026-03-25   |   51.7°F |   37.5°F |   0.028inch
...
```

---

## Error Handling

| Situation | Response |
|-----------|----------|
| No internet / DNS failure | "Could not connect…" + exit |
| Request times out (10 s) | "Request timed out…" + exit |
| Server returns HTTP error | HTTP status message + exit |
| City name not found | "Location not found…" + exit |
| City found, wrong state | "Not found in the United States" + exit |
| Blank city or state | "Cannot be blank" + exit |

---

## APIs Used

| API | URL | Key required? |
|-----|-----|--------------|
| Geocoding | `https://geocoding-api.open-meteo.com/v1/search` | No |
| Forecast  | `https://api.open-meteo.com/v1/forecast`         | No |

---

## File Layout

```
weather_forecast/
├── weather_forecast.py   ← Main application
├── requirements.txt      ← pip dependency list
└── README.md             ← This file
```

---

## Learning Notes

- **`requests.get(url, params=…)`** — builds and sends an HTTP GET
  request; `params=` handles URL-encoding the query string for you.
- **`response.raise_for_status()`** — raises an exception for any
  4xx/5xx HTTP response so you don't silently process error pages.
- **`response.json()`** — parses the response body from JSON text
  into a Python dictionary automatically.
- **`zip(a, b, c, d)`** — iterates over multiple lists in parallel,
  so all values at index 0 belong to day 1, index 1 to day 2, etc.
- **`sys.exit(1)`** — immediately terminates the program with exit
  code 1 (convention for "something went wrong").
