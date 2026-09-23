import os
import requests
from langchain.tools import tool
from dotenv import load_dotenv


load_dotenv()


API_KEY = (
    os.getenv("FLIGHTAPI_KEY")
    or os.getenv("FLIGHT_API_KEY")
    or os.getenv("FLIGHT_MCP_API_KEY")
)


def _normalize_lookup(data_item: list | dict | None, key_attr: str = "id") -> dict:
    """Normalize a list-of-dicts or dict into an ID-based dictionary lookup."""
    if not data_item:
        return {}
    if isinstance(data_item, dict):
        result = {}
        for k, v in data_item.items():
            result[str(k)] = v
            if isinstance(v, dict) and key_attr in v:
                result[str(v[key_attr])] = v
        return result
    if isinstance(data_item, list):
        result = {}
        for item in data_item:
            if isinstance(item, dict):
                item_id = item.get(key_attr)
                if item_id is not None:
                    result[str(item_id)] = item
        return result
    return {}


def format_flightapi_response(
    data: dict,
    origin_code: str,
    destination_code: str,
    departure_date: str,
    adults: int = 1,
    cabin_class: str = "Economy",
    currency: str = "INR",
) -> dict:
    """Format FlightAPI.io normalized relational response into a clean structure."""
    if not isinstance(data, dict):
        return {
            "success": False,
            "origin": origin_code,
            "destination": destination_code,
            "departure_date": departure_date,
            "offers": [],
            "error": "Invalid response format received from FlightAPI.",
        }

    # Handle FlightAPI error payloads (e.g. {"message": "Invalid API key"})
    if "message" in data and not data.get("itineraries"):
        return {
            "success": False,
            "origin": origin_code,
            "destination": destination_code,
            "departure_date": departure_date,
            "offers": [],
            "error": f"FlightAPI error: {data['message']}",
        }

    itineraries = data.get("itineraries", [])
    if not itineraries:
        return {
            "success": True,
            "origin": origin_code,
            "destination": destination_code,
            "departure_date": departure_date,
            "adults": adults,
            "total_offers": 0,
            "offers": [],
            "message": f"No flights found between {origin_code} and {destination_code} for {departure_date}.",
        }

    legs_lookup = _normalize_lookup(data.get("legs"))
    segments_lookup = _normalize_lookup(data.get("segments"))
    carriers_lookup = _normalize_lookup(data.get("carriers"))

    offers = []

    for itinerary in itineraries:
        pricing_options = itinerary.get("pricing_options", [])
        if not pricing_options:
            continue

        # Find the cheapest pricing option
        cheapest_option = None
        min_price = float("inf")

        for opt in pricing_options:
            price_info = opt.get("price", {})
            amt = price_info.get("amount")
            if amt is not None:
                try:
                    amt_float = float(amt)
                    if amt_float < min_price:
                        min_price = amt_float
                        cheapest_option = opt
                except (ValueError, TypeError):
                    pass

        if cheapest_option is None:
            cheapest_option = pricing_options[0]
            amt = cheapest_option.get("price", {}).get("amount", 0)
            try:
                min_price = float(amt)
            except (ValueError, TypeError):
                min_price = 0.0

        # Extract deep link / booking URL
        booking_url = None
        items = cheapest_option.get("items", [])
        if items and isinstance(items, list) and isinstance(items[0], dict):
            booking_url = items[0].get("url")
        if not booking_url:
            booking_url = cheapest_option.get("deepLink") or itinerary.get("deepLink")

        # Resolve outbound leg
        leg_ids = itinerary.get("leg_ids", [])
        leg = {}
        if leg_ids:
            leg = legs_lookup.get(str(leg_ids[0]), {})

        # Resolve segments within this leg
        segment_ids = leg.get("segment_ids", [])
        segments = [
            segments_lookup.get(str(seg_id), {})
            for seg_id in segment_ids
            if str(seg_id) in segments_lookup
        ]

        first_segment = segments[0] if segments else {}
        last_segment = segments[-1] if segments else {}

        # Resolve marketing / operating carrier
        carrier_id = (
            first_segment.get("marketing_carrier_id")
            or first_segment.get("operating_carrier_id")
            or (leg.get("marketing_carrier_ids", [None])[0] if leg.get("marketing_carrier_ids") else None)
        )

        airline_name = "Unknown Airline"
        carrier_code = ""

        if carrier_id is not None:
            carrier = carriers_lookup.get(str(carrier_id), {})
            if carrier:
                airline_name = carrier.get("name") or carrier.get("alt_id") or airline_name
                carrier_code = carrier.get("display_code") or carrier.get("iata") or ""

        # Flight number
        flight_num_raw = first_segment.get("marketing_flight_number") or ""
        if carrier_code and flight_num_raw:
            flight_number = f"{carrier_code} {flight_num_raw}".strip()
        elif flight_num_raw:
            flight_number = str(flight_num_raw)
        elif carrier_code:
            flight_number = carrier_code
        else:
            flight_number = "N/A"

        # Timing and duration
        departure_time = leg.get("departure") or first_segment.get("departure")
        arrival_time = leg.get("arrival") or last_segment.get("arrival")
        duration_minutes = leg.get("duration")

        # Stops count
        if "stop_count" in leg:
            stops = leg.get("stop_count")
        elif segment_ids:
            stops = max(0, len(segment_ids) - 1)
        else:
            stops = 0

        offers.append({
            "airline": airline_name,
            "flight_number": flight_number,
            "price": round(min_price, 2),
            "currency": currency.upper(),
            "departure": departure_time,
            "arrival": arrival_time,
            "duration_minutes": duration_minutes,
            "stops": stops,
            "cabin": cabin_class,
            "booking_link": booking_url,
        })

    # Sort offers by lowest price first
    offers.sort(key=lambda x: x["price"] if x["price"] > 0 else float("inf"))

    return {
        "success": True,
        "origin": origin_code,
        "destination": destination_code,
        "departure_date": departure_date,
        "adults": adults,
        "cabin": cabin_class,
        "currency": currency.upper(),
        "total_offers": len(offers),
        "offers": offers[:10],
    }


# Backward compatibility alias
format_flight_response = format_flightapi_response

IATA_CODES = {
    "mumbai": "BOM",
    "bombay": "BOM",
    "delhi": "DEL",
    "new delhi": "DEL",
    "goa": "GOI",
    "dabolim": "GOI",
    "mopa": "GOX",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "pune": "PNQ",
    "hyderabad": "HYD",
    "chennai": "MAA",
    "madras": "MAA",
    "kolkata": "CCU",
    "calcutta": "CCU",
    "ahmedabad": "AMD",
    "jaipur": "JAI",
    "kochi": "COK",
    "cochin": "COK",
    "thiruvananthapuram": "TRV",
    "trivandrum": "TRV",
    "lucknow": "LKO",
    "varanasi": "VNS",
    "chandigarh": "IXC",
    "amritsar": "ATQ",
    "srinagar": "SXR",
    "udaipur": "UDR",
    "patna": "PAT",
    "guwahati": "GAU",
    "indore": "IDR",
    "bhopal": "BHO",
    "surat": "STV",
    "nagpur": "NAG",
    "visakhapatnam": "VTZ",
    "mangalore": "IXE",
    "coimbatore": "CJB",
    "madurai": "IXM",
    "dubai": "DXB",
    "london": "LHR",
    "singapore": "SIN",
    "bangkok": "BKK",
    "new york": "JFK",
    "san francisco": "SFO",
    "paris": "CDG",
    "tokyo": "NRT",
    "bali": "DPS",
    "denpasar": "DPS",
    "phuket": "HKT",
    "kuala lumpur": "KUL",
}


def resolve_iata(code_or_city: str) -> str:
    """Resolve a city name or code to a 3-letter uppercase IATA code."""
    cleaned = code_or_city.strip()
    if len(cleaned) == 3 and cleaned.isalpha():
        return cleaned.upper()
    return IATA_CODES.get(cleaned.lower(), cleaned.upper())


@tool
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str | None = None,
    adults: int = 1,
    cabin_class: str = "Economy",
    currency: str = "INR",
) -> dict:
    """
    Search for flight offers between two airports using FlightAPI.io.

    Args:
        origin: Origin city or 3-letter IATA code (e.g., "Mumbai" or "BOM", "Delhi" or "DEL").
        destination: Destination city or 3-letter IATA code (e.g., "Goa" or "GOI", "Bangalore" or "BLR").
        departure_date: Departure date in YYYY-MM-DD format (must be a current or upcoming date).
        return_date: Optional return date in YYYY-MM-DD format for round trips.
        adults: Number of adult passengers (default: 1).
        cabin_class: Travel class: "Economy", "Business", "First", or "Premium_Economy" (default: "Economy").
        currency: 3-letter currency code (e.g., "INR", "USD", "EUR") (default: "INR").
    """

    api_key = (
        API_KEY
        or os.getenv("FLIGHTAPI_KEY")
        or os.getenv("FLIGHT_API_KEY")
        or os.getenv("FLIGHT_MCP_API_KEY")
    )

    if not api_key:
        return {
            "success": False,
            "origin": origin,
            "destination": destination,
            "offers": [],
            "error": (
                "FLIGHTAPI_KEY is not configured in the .env file. "
                "Please obtain an API key from https://www.flightapi.io and set FLIGHTAPI_KEY in .env."
            ),
        }

    origin_code = resolve_iata(origin)
    destination_code = resolve_iata(destination)

    if len(origin_code) != 3 or not origin_code.isalpha():
        return {
            "success": False,
            "origin": origin,
            "destination": destination,
            "offers": [],
            "error": (
                f"Could not identify a commercial airport for origin city '{origin}'. "
                "Please clarify the departure city name (e.g., Mumbai, Delhi, Pune)."
            ),
        }

    if len(destination_code) != 3 or not destination_code.isalpha():
        return {
            "success": False,
            "origin": origin,
            "destination": destination,
            "offers": [],
            "error": (
                f"Could not identify a commercial airport for destination city '{destination}'. "
                "Please clarify the destination city name (e.g., Goa, Bangalore, Delhi)."
            ),
        }

    # Normalize cabin class as required by FlightAPI.io
    cabin_map = {
        "economy": "Economy",
        "business": "Business",
        "first": "First",
        "premium_economy": "Premium_Economy",
        "premiumeconomy": "Premium_Economy",
        "premium economy": "Premium_Economy",
    }
    normalized_cabin = cabin_map.get(cabin_class.strip().lower(), "Economy")
    normalized_currency = currency.strip().upper() if currency else "INR"
    children = 0
    infants = 0

    # Build FlightAPI.io URL
    # One-way Trip API: https://api.flightapi.io/onewaytrip/<api_key>/<dep>/<arr>/<date>/<adults>/<children>/<infants>/<cabin>/<currency>
    # Round-trip API:   https://api.flightapi.io/roundtrip/<api_key>/<dep>/<arr>/<date>/<return_date>/<adults>/<children>/<infants>/<cabin>/<currency>
    if return_date:
        url = (
            f"https://api.flightapi.io/roundtrip/{api_key}/{origin_code}/{destination_code}/"
            f"{departure_date}/{return_date}/{adults}/{children}/{infants}/{normalized_cabin}/{normalized_currency}"
        )
    else:
        url = (
            f"https://api.flightapi.io/onewaytrip/{api_key}/{origin_code}/{destination_code}/"
            f"{departure_date}/{adults}/{children}/{infants}/{normalized_cabin}/{normalized_currency}"
        )

    headers = {
        "Accept": "application/json",
    }

    response = None

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30,
        )

        if response.status_code in (401, 403):
            return {
                "success": False,
                "origin": origin_code,
                "destination": destination_code,
                "departure_date": departure_date,
                "offers": [],
                "error": "FlightAPI authorization failed (401/403). Please verify your FLIGHTAPI_KEY in the .env file.",
            }

        if response.status_code in (402, 429):
            return {
                "success": False,
                "origin": origin_code,
                "destination": destination_code,
                "departure_date": departure_date,
                "offers": [],
                "error": "FlightAPI credit quota exceeded or rate limit reached. Each search consumes 2 credits.",
            }

        response.raise_for_status()

        data = response.json()

        return format_flightapi_response(
            data=data,
            origin_code=origin_code,
            destination_code=destination_code,
            departure_date=departure_date,
            adults=adults,
            cabin_class=normalized_cabin,
            currency=normalized_currency,
        )

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "origin": origin_code,
            "destination": destination_code,
            "departure_date": departure_date,
            "offers": [],
            "error": "Flight search request timed out. FlightAPI took too long to aggregate prices.",
        }

    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if response is not None:
            try:
                err_data = response.json()
                if isinstance(err_data, dict):
                    error_msg = err_data.get("message") or err_data.get("error") or response.text
                else:
                    error_msg = response.text
            except Exception:
                error_msg = response.text

        return {
            "success": False,
            "origin": origin_code,
            "destination": destination_code,
            "departure_date": departure_date,
            "offers": [],
            "error": f"Flight search failed: {error_msg}",
        }

    except Exception as e:
        return {
            "success": False,
            "origin": origin_code,
            "destination": destination_code,
            "departure_date": departure_date,
            "offers": [],
            "error": f"Unexpected error during flight search: {str(e)}",
        }


# Alias for backwards compatibility
fetch_flight_information = search_flights


if __name__ == "__main__":
    result = search_flights.invoke({
        "origin": "Mumbai",
        "destination": "Goa",
        "departure_date": "2026-10-15",
        "adults": 2,
    })
    print(result)