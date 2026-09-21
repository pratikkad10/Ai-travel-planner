import requests
from langchain_core.tools import tool
from utils.geo import get_coordinates


def get_weather(latitude: float, longitude: float) -> dict:
    """Get current weather and 7-day forecast for coordinates."""

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m"
        ),
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "precipitation_probability_max"
        ),
        "timezone": "auto",
        "forecast_days": 7,
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Weather service timed out. Please try again."
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Weather service is temporarily unavailable: {e}"
        }
        

@tool
def fetch_weather_forecast(location: str) -> dict:
    """
    Get current weather and a 7-day forecast for a location.

    The location can be a city, town, village, state, or country.

    Args:
        location: Name of the location, such as
                  "Panaji, Goa" or "Nashik, India".
    """

    coordinates = get_coordinates(location)

    weather = get_weather(
        latitude=coordinates["latitude"],
        longitude=coordinates["longitude"],
    )

    return {
        "location": {
            "name": coordinates["name"],
            "city": coordinates["city"],
            "state": coordinates["state"],
            "country": coordinates["country"],
        },
        "coordinates": {
            "latitude": coordinates["latitude"],
            "longitude": coordinates["longitude"],
        },
        "timezone": weather.get("timezone"),
        "current": weather.get("current"),
        "daily": weather.get("daily"),
    }


if __name__ == "__main__":

    result = fetch_weather_forecast.invoke({
        "location": "Panaji, Goa"
    })

    print(result)