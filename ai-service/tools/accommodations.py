import os
import requests
from dotenv import load_dotenv
from langchain.tools import tool
from utils.geo import get_coordinates

load_dotenv()

API_KEY = os.getenv("GEOAPIFY_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEOAPIFY_API_KEY is not configured in the .env file."
    )

def search_hotels(location: str) -> dict:
    """
    Search for hotels in a given location.
    """
    try:
        coordinates = get_coordinates(location)

        url = "https://api.geoapify.com/v2/places"

        params = {
            "categories": "accommodation.hotel",
            "filter": f"circle:{coordinates['longitude']},{coordinates['latitude']},5000",
            "limit": 10,
            "apiKey": API_KEY,
            "bias": (
                f"proximity:"
                f"{coordinates['longitude']},"
                f"{coordinates['latitude']}"
            ),
        }

        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()
        features = data.get("features", [])

        if not features:
            return {
                "location": location,
                "coordinates": coordinates,
                "hotels": [],
                "message": f"No hotels found near {location}.",
            }

        hotels = []
        for feature in features:
            properties = feature.get("properties", {})
            hotels.append({
                "place_id": properties.get("place_id"),
                "name": properties.get("name"),
                "address": properties.get("address_line1"),
                "city": properties.get("city"),
                "state": properties.get("state"),
                "country": properties.get("country"),
                "latitude": properties.get("lat"),
                "longitude": properties.get("lon"),
                "rating": properties.get("rating"),
                "price_level": properties.get("price_level"),
            })

        return {
            "location": location,
            "coordinates": coordinates,
            "hotels": hotels,
        }
    except Exception as e:
        return {
            "location": location,
            "hotels": [],
            "error": f"Failed to search hotels: {str(e)}",
        }

@tool
def search_hotel_places(location: str) -> dict:
    """
    Find hotels in a given city or location.

    Args:
        location: City, area, or location where hotels are required.
    """

    return search_hotels(location)


# if __name__ == "__main__":
#     result = search_hotel_places.invoke({
#         "location": "Pune, India"
#     })

#     print(result)
