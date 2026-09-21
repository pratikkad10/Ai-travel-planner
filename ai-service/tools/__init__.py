from tools.accommodations import search_hotel_places
from tools.calculator import add, subtract, multiply, divide, percentage
from tools.currency import fetch_currency_exchange_rate
from tools.flights import search_flights
from tools.places import search_places, search_restaurants, get_place_details
from tools.weather import fetch_weather_forecast, get_weather

ALL_TOOLS = [
    fetch_currency_exchange_rate,
    add,
    subtract,
    multiply,
    divide,
    percentage,
    search_flights,
    search_hotel_places,
    search_restaurants,
    search_places,
    get_place_details,
    fetch_weather_forecast,
]

__all__ = [
    "search_hotel_places",
    "add",
    "subtract",
    "multiply",
    "divide",
    "percentage",
    "fetch_currency_exchange_rate",
    "search_flights",
    "search_places",
    "search_restaurants",
    "get_place_details",
    "fetch_weather_forecast",
    "get_weather",
    "ALL_TOOLS",
]
