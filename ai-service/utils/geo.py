import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")


def get_coordinates(location: str) -> dict:
    """
    Get latitude, longitude, and address details for a given location using Geoapify.

    Args:
        location: City, area, or address to geocode.

    Returns:
        dict: Geocoded information including latitude, longitude, name, city, state, and country.

    Raises:
        RuntimeError: If GEOAPIFY_API_KEY is missing or the request fails.
        ValueError: If the location is not found.
    """
    if not GEOAPIFY_API_KEY:
        raise RuntimeError("GEOAPIFY_API_KEY is not configured in the .env file.")

    url = "https://api.geoapify.com/v1/geocode/search"
    params = {
        "text": location,
        "format": "json",
        "limit": 1,
        "apiKey": GEOAPIFY_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout as e:
        raise RuntimeError("Geocoding request timed out.") from e
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Geocoding request failed: {e}") from e

    data = response.json()
    results = data.get("results")

    if not results:
        raise ValueError(f"Location not found: {location}")

    result = results[0]

    return {
        "name": result.get("formatted", location),
        "city": result.get("city"),
        "state": result.get("state"),
        "country": result.get("country"),
        "latitude": result["lat"],
        "longitude": result["lon"],
    }
