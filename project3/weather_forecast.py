"""
weather_forecast.py
-------------------
Console application that prompts the user for a US city and state,
then retrieves and displays a 10-day weather forecast using two
free APIs:

  1. Open-Meteo Geocoding API  – converts city + state → lat/lon
     https://open-meteo.com/en/docs/geocoding-api

  2. Open-Meteo Forecast API   – returns daily forecast data
     https://open-meteo.com/en/docs

No API key is required for either endpoint.

Usage:
    python weather_forecast.py

Dependencies:
    pip install requests
"""

import sys        # Used to call sys.exit() when we need to stop the program early
import requests   # Third-party library for making HTTP requests to web APIs


# ------------------------------------------------------------------
# CONSTANTS  –  API base URLs and request timeout (seconds).
# Keeping them here makes them easy to update if the URLs ever change.
# ------------------------------------------------------------------
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL  = "https://api.open-meteo.com/v1/forecast"
TIMEOUT       = 10   # Seconds to wait before treating the request as failed


# ==================================================================
#  STEP 1 – GEOCODING
#  Convert a city name + state name into a latitude and longitude.
# ==================================================================

def geocode_city(city: str, state: str) -> tuple[float, float, str]:
    """
    Query the Open-Meteo Geocoding API for the given city, then
    filter the results to the one located in the requested US state.

    Why filter by state?
    --------------------
    The geocoding API returns results from the entire world.
    Searching for "Birmingham" would match both Birmingham, Alabama
    and Birmingham, England.  By checking the `admin1` field
    (which Open-Meteo uses for US states) we ensure we get the
    correct US location.

    Parameters
    ----------
    city  : str  – City name entered by the user (e.g. "Birmingham")
    state : str  – State name entered by the user (e.g. "Alabama")

    Returns
    -------
    (latitude, longitude, display_name) as a tuple

    Exits the program (sys.exit) if:
      - A network error occurs
      - No results are returned
      - None of the results match the requested state
    """

    # Build the query parameters that will be appended to the URL.
    # count=10 asks for up to 10 candidate matches so we have enough
    # results to filter through for the correct state.
    params = {
        "name":     city,
        "count":    10,
        "language": "en",
        "format":   "json"
    }

    # ---- Make the HTTP GET request ----------------------------------
    try:
        # requests.get() sends the request; params= handles URL encoding
        response = requests.get(GEOCODING_URL, params=params, timeout=TIMEOUT)

        # raise_for_status() turns any 4xx / 5xx HTTP response into an
        # exception so we don't silently process a failed response
        response.raise_for_status()

    except requests.exceptions.ConnectionError:
        # Couldn't reach the server at all (no internet, DNS failure, etc.)
        print("ERROR: Could not connect to the geocoding service.")
        print("       Please check your internet connection and try again.")
        sys.exit(1)

    except requests.exceptions.Timeout:
        # The server took too long to respond
        print(f"ERROR: The geocoding request timed out after {TIMEOUT} seconds.")
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        # The server responded but with an error status code (e.g. 500)
        print(f"ERROR: Geocoding API returned an error: {e}")
        sys.exit(1)

    except requests.exceptions.RequestException as e:
        # Catch-all for any other requests-related problem
        print(f"ERROR: An unexpected network error occurred: {e}")
        sys.exit(1)

    # ---- Parse the JSON response ------------------------------------
    data = response.json()

    # The API wraps results in a "results" key; if it's missing or
    # empty, no locations were found for the city name at all.
    results = data.get("results", [])
    if not results:
        print(f"ERROR: Location '{city}' was not found. Please check the city name.")
        sys.exit(1)

    # ---- Filter to the correct US state -----------------------------
    # Each result has:
    #   country_code – "US" for United States
    #   admin1       – State name for US results (e.g. "Alabama")
    #
    # We compare in lowercase so capitalisation differences don't matter
    # (the user might type "alabama" or "Alabama" – both should match).
    state_lower = state.strip().lower()

    match = None
    for result in results:
        country = result.get("country_code", "")
        admin1  = result.get("admin1", "").lower()

        if country == "US" and admin1 == state_lower:
            match = result
            break   # Stop at the first (highest-relevance) match

    if match is None:
        # We found the city name but not in the requested state
        print(f"ERROR: '{city}, {state}' was not found in the United States.")
        print("       Please verify the city and state names and try again.")
        sys.exit(1)

    # Pull the coordinates and a human-readable name from the result
    latitude     = match["latitude"]
    longitude    = match["longitude"]
    display_name = f"{match['name']}, {match.get('admin1', state)}"

    return latitude, longitude, display_name


# ==================================================================
#  STEP 2 – FORECAST
#  Use the coordinates to fetch a 10-day daily forecast.
# ==================================================================

def get_forecast(latitude: float, longitude: float) -> dict:
    """
    Query the Open-Meteo Forecast API for a 10-day daily forecast
    at the given coordinates.

    Parameters
    ----------
    latitude  : float – Latitude from the geocoding step
    longitude : float – Longitude from the geocoding step

    Returns
    -------
    A Python dictionary containing the full API JSON response.

    Exits the program on any network or HTTP error.
    """

    # Request the specific daily variables we want to display:
    #   temperature_2m_max   – daily high temperature
    #   temperature_2m_min   – daily low temperature
    #   precipitation_sum    – total precipitation for the day
    params = {
        "latitude":            latitude,
        "longitude":           longitude,
        "daily":               "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "temperature_unit":    "fahrenheit",   # Requirement: Fahrenheit
        "precipitation_unit":  "inch",         # Requirement: inches
        "timezone":            "America/New_York",  # Keeps dates local to the US East coast;
                                                    # open-meteo defaults to UTC
        "forecast_days":       10              # Requirement: 10-day forecast
    }

    # ---- Make the HTTP GET request ----------------------------------
    try:
        response = requests.get(FORECAST_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the forecast service.")
        print("       Please check your internet connection and try again.")
        sys.exit(1)

    except requests.exceptions.Timeout:
        print(f"ERROR: The forecast request timed out after {TIMEOUT} seconds.")
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"ERROR: Forecast API returned an error: {e}")
        sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"ERROR: An unexpected network error occurred: {e}")
        sys.exit(1)

    return response.json()


# ==================================================================
#  STEP 3 – DISPLAY
#  Format and print the forecast data as a table.
# ==================================================================

def display_forecast(display_name: str, forecast_data: dict) -> None:
    """
    Extract the daily forecast arrays from the API response and
    print them as a neatly aligned table.

    Parameters
    ----------
    display_name  : str  – Human-readable location label for the header
    forecast_data : dict – Full JSON response from the Forecast API
    """

    # The daily forecast values live inside forecast_data["daily"]
    daily = forecast_data.get("daily", {})

    # Each key maps to a list with one value per forecast day
    dates     = daily.get("time",                [])   # List of date strings, e.g. "2026-03-13"
    max_temps = daily.get("temperature_2m_max",  [])   # Daily high temperatures in °F
    min_temps = daily.get("temperature_2m_min",  [])   # Daily low temperatures in °F
    precip    = daily.get("precipitation_sum",   [])   # Daily precipitation in inches

    # Safety check – if the API returned no data, alert the user
    if not dates:
        print("ERROR: No forecast data was returned by the API.")
        sys.exit(1)

    # ---- Print the header -------------------------------------------
    print(f"\n--- 10-Day Forecast for {display_name} ---")

    # Column headers and separator line (matches the sample output format)
    print(f"{'Date':<12} | {'Max Temp':>8} | {'Min Temp':>8} | {'Rain':>10}")
    print("-" * 50)

    # ---- Print one row per forecast day -----------------------------
    # zip() lets us iterate over all four lists in parallel so that
    # dates[0], max_temps[0], min_temps[0], precip[0] always refer to
    # the same day.
    for date, high, low, rain in zip(dates, max_temps, min_temps, precip):

        # The API can occasionally return None for a value if data is
        # unavailable; we replace None with 0.0 to avoid crashes.
        high = high if high is not None else 0.0
        low  = low  if low  is not None else 0.0
        rain = rain if rain is not None else 0.0

        # Format each row:
        #   :<12   – left-align the date in a 12-character field
        #   :>8    – right-align temperatures in an 8-character field
        #   :>10   – right-align precipitation in a 10-character field
        print(
            f"{date:<12} | "
            f"{high:>6.1f}°F | "
            f"{low:>6.1f}°F | "
            f"{rain:>7.3f}inch"
        )

    print()   # Trailing blank line for a clean exit


# ==================================================================
#  MAIN  –  tie all the steps together
# ==================================================================

def main() -> None:
    """
    Entry point of the application.

    1. Prompt the user for city and state
    2. Geocode the location (get coordinates)
    3. Fetch the 10-day forecast
    4. Display the forecast table
    """

    print("=== 10-Day Weather Forecast ===\n")

    # ---- Get user input ---------------------------------------------
    # .strip() removes any accidental leading/trailing whitespace
    city  = input("Enter city:  ").strip()
    state = input("Enter state: ").strip()

    # Basic check – make sure neither field was left blank
    if not city or not state:
        print("ERROR: City and state cannot be blank.")
        sys.exit(1)

    # ---- Step 1: Geocode --------------------------------------------
    # Converts the city + state text into GPS coordinates and a
    # confirmed display name (e.g. "Lynchburg, Virginia")
    print(f"\nLooking up '{city}, {state}'...")
    latitude, longitude, display_name = geocode_city(city, state)

    # ---- Step 2: Fetch forecast -------------------------------------
    print(f"Fetching 10-day forecast for {display_name}...")
    forecast_data = get_forecast(latitude, longitude)

    # ---- Step 3: Display --------------------------------------------
    display_forecast(display_name, forecast_data)


# ------------------------------------------------------------------
# Only call main() when this script is run directly.
# If another script imports this module, main() won't run
# automatically (a Python best-practice).
# ------------------------------------------------------------------
if __name__ == "__main__":
    main()
