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


CATEGORY_MAPPING = {
    "restaurant": "catering.restaurant",
    "restaurants": "catering.restaurant",
    "tourism.restaurant": "catering.restaurant",
    "food": "catering.restaurant",
    "dining": "catering.restaurant",
    "cafe": "catering.cafe",
    "cafes": "catering.cafe",
    "coffee": "catering.cafe",
    "bar": "catering.bar",
    "bars": "catering.bar",
    "pub": "catering.pub",
    "attraction": "tourism.attraction",
    "attractions": "tourism.attraction",
    "sights": "tourism.sights",
    "hotel": "accommodation.hotel",
    "hotels": "accommodation.hotel",
}


def search_places_api(
    location: str,
    category: str = "tourism.attraction",
) -> dict:
    """
    Search for places and attractions around a location.

    Args:
        location: City, area, or place to search around.
        category: Type of place to search for.
    """
    try:
        normalized_category = CATEGORY_MAPPING.get(
            category.lower().strip(), category
        )

        coordinates = get_coordinates(location)
        latitude = coordinates["latitude"]
        longitude = coordinates["longitude"]

        url = "https://api.geoapify.com/v2/places"

        params = {
            "categories": normalized_category,
            "filter": f"circle:{longitude},{latitude},5000",
            "bias": f"proximity:{longitude},{latitude}",
            "limit": 10,
            "apiKey": API_KEY,
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
                "category": normalized_category,
                "count": 0,
                "places": [],
                "message": f"No places found for {location} under category '{normalized_category}'.",
            }

        places = []
        for feature in features:
            properties = feature.get("properties", {})
            datasource = properties.get("datasource", {})
            raw = datasource.get("raw", {})
            contact = properties.get("contact", {})
            catering = properties.get("catering", {})
            facilities = properties.get("facilities", {})

            cuisine = (
                catering.get("cuisine")
                or raw.get("cuisine")
                or properties.get("cuisine")
            )
            opening_hours = (
                properties.get("opening_hours")
                or raw.get("opening_hours")
            )
            phone = contact.get("phone") or raw.get("phone")
            website = (
                contact.get("website")
                or properties.get("website")
                or raw.get("website")
            )
            rating = (
                properties.get("rating")
                or raw.get("stars")
                or raw.get("rating")
            )
            popularity = properties.get("rank", {}).get("popularity")

            facility_list = []
            if catering.get("outdoor_seating") or raw.get("outdoor_seating") == "yes":
                facility_list.append("outdoor_seating")
            if catering.get("takeaway") or raw.get("takeaway") == "yes":
                facility_list.append("takeaway")
            if catering.get("delivery") or raw.get("delivery") == "yes":
                facility_list.append("delivery")
            if facilities.get("wheelchair") or raw.get("wheelchair") == "yes":
                facility_list.append("wheelchair_accessible")
            if facilities.get("internet_access") or raw.get("internet_access") == "wlan":
                facility_list.append("wifi")

            places.append({
                "place_id": properties.get("place_id"),
                "name": properties.get("name"),
                "address": properties.get("formatted"),
                "city": properties.get("city"),
                "state": properties.get("state"),
                "country": properties.get("country"),
                "latitude": properties.get("lat"),
                "longitude": properties.get("lon"),
                "distance_meters": properties.get("distance"),
                "categories": properties.get("categories", []),
                "cuisine": cuisine,
                "opening_hours": opening_hours,
                "phone": phone,
                "website": website,
                "rating": rating,
                "popularity": popularity,
                "facilities": facility_list,
            })

        return {
            "location": location,
            "category": normalized_category,
            "count": len(places),
            "places": places,
        }

    except Exception as e:
        return {
            "location": location,
            "category": category,
            "count": 0,
            "places": [],
            "error": f"Failed to search places: {str(e)}",
        }


def get_place_details_api(place_id: str) -> dict:
    """
    Get detailed information about a specific place using its place_id from Geoapify.

    Args:
        place_id: Unique identifier of the place.
    """
    try:
        url = "https://api.geoapify.com/v2/place-details"
        params = {
            "id": place_id,
            "apiKey": API_KEY,
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        features = data.get("features", [])

        if not features:
            return {
                "place_id": place_id,
                "error": f"No details found for place_id: {place_id}",
            }

        properties = features[0].get("properties", {})
        datasource = properties.get("datasource", {})
        raw = datasource.get("raw", {})
        contact = properties.get("contact", {})
        catering = properties.get("catering", {})
        facilities = properties.get("facilities", {})
        wiki = properties.get("wiki_and_media", {})

        cuisine = (
            catering.get("cuisine")
            or raw.get("cuisine")
            or properties.get("cuisine")
        )
        phone = contact.get("phone") or raw.get("phone")
        website = (
            contact.get("website")
            or properties.get("website")
            or raw.get("website")
        )
        email = contact.get("email") or raw.get("email")
        opening_hours = (
            properties.get("opening_hours")
            or raw.get("opening_hours")
        )
        rating = (
            properties.get("rating")
            or raw.get("stars")
            or raw.get("rating")
        )
        popularity = properties.get("rank", {}).get("popularity")

        facility_list = []
        if catering.get("outdoor_seating") or raw.get("outdoor_seating") == "yes":
            facility_list.append("outdoor_seating")
        if catering.get("takeaway") or raw.get("takeaway") == "yes":
            facility_list.append("takeaway")
        if catering.get("delivery") or raw.get("delivery") == "yes":
            facility_list.append("delivery")
        if facilities.get("wheelchair") or raw.get("wheelchair") == "yes":
            facility_list.append("wheelchair_accessible")
        if facilities.get("internet_access") or raw.get("internet_access") == "wlan":
            facility_list.append("wifi")

        return {
            "place_id": place_id,
            "name": properties.get("name"),
            "address": properties.get("formatted"),
            "city": properties.get("city"),
            "state": properties.get("state"),
            "country": properties.get("country"),
            "postcode": properties.get("postcode"),
            "latitude": properties.get("lat"),
            "longitude": properties.get("lon"),
            "categories": properties.get("categories", []),
            "cuisine": cuisine,
            "opening_hours": opening_hours,
            "phone": phone,
            "email": email,
            "website": website,
            "rating": rating,
            "popularity": popularity,
            "facilities": facility_list,
            "description": wiki.get("description"),
            "wikipedia": wiki.get("wikipedia"),
        }

    except Exception as e:
        return {
            "place_id": place_id,
            "error": f"Failed to retrieve place details: {str(e)}",
        }


@tool
def get_place_details(place_id: str) -> dict:
    """
    Get detailed information about a specific place or restaurant using its place_id.

    Use this tool when the user asks for more details (such as phone number, website,
    opening hours, cuisine, facilities, or description) about a specific place or restaurant.

    Args:
        place_id: The unique place_id of the place (obtained from search_places, search_restaurants, or search_hotel_places).
    """
    return get_place_details_api(place_id=place_id)


@tool
def search_places(
    location: str,
    category: str = "tourism.attraction",
) -> dict:
    """
    Search for places, attractions, restaurants, or cafes around a location.

    Args:
        location: City, area, or place to search around.
        category: Type of place to search for. Supported categories include:
                  - "catering.restaurant" (or "restaurant") for dining and restaurants
                  - "catering.cafe" (or "cafe") for cafes and coffee shops
                  - "tourism.attraction" (or "attraction") for tourist attractions and sights
                  - "tourism.sights" for landmarks
    """
    return search_places_api(
        location=location,
        category=category,
    )


@tool
def search_restaurants(location: str) -> dict:
    """
    Search for restaurants, dining places, and eateries in a given location.

    Args:
        location: City, area, or location where restaurants are required.
    """
    return search_places_api(
        location=location,
        category="catering.restaurant",
    )


if __name__ == "__main__":
    result = search_places.invoke({
        "location": "Pune, India",
        "category": "tourism.attraction",
    })
    print(result)

    restaurant_result = search_restaurants.invoke({
        "location": "Panaji, Goa",
    })
    print(restaurant_result)