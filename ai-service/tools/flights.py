import os
import requests
from langchain.tools import tool
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("FLIGHT_MCP_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "FLIGHT_MCP_API_KEY is not configured in the .env file."
    )


def format_flight_response(data: dict) -> dict:
    """Format raw Flight MCP response into a clean structure."""

    offers = []

    for offer in data.get("offers", []):

        price = offer.get("price", {})

        itinerary = offer.get("itineraries", [{}])[0]
        segments = itinerary.get("segments", [])

        if not segments:
            continue

        first_segment = segments[0]
        last_segment = segments[-1]

        offers.append({
            "airline": first_segment.get(
                "marketingCarrier", {}
            ).get("name"),

            "flight_number": first_segment.get(
                "flightNumber"
            ),

            "price": price.get(
                "amountMinor", 0
            ) / 100,

            "currency": price.get("currency"),

            "departure": first_segment.get(
                "departureAt"
            ),

            "arrival": last_segment.get(
                "arrivalAt"
            ),

            "duration_minutes": itinerary.get(
                "durationMinutes"
            ),

            "stops": itinerary.get(
                "stops"
            ),

            "cabin": offer.get(
                "cabinClass"
            ),
        })

    return {
        "origin": data.get("query", {}).get("origin"),
        "destination": data.get("query", {}).get("destination"),
        "departure_date": data.get("query", {}).get("departureDate"),
        "adults": data.get("query", {}).get("adults"),
        "offers": offers,
    }

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
    "dubai": "DXB",
    "london": "LHR",
    "singapore": "SIN",
    "bangkok": "BKK",
    "new york": "JFK",
    "san francisco": "SFO",
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
) -> dict:
    """
    Search for flight offers between two airports.

    Args:
        origin: Origin airport 3-letter IATA code (e.g., "BOM" for Mumbai, "DEL" for Delhi, "PNQ" for Pune).
        destination: Destination airport 3-letter IATA code (e.g., "GOI" for Goa, "BLR" for Bangalore).
        departure_date: Departure date in YYYY-MM-DD format.
        return_date: Optional return date in YYYY-MM-DD format.
        adults: Number of adult passengers (default: 1).
    """

    origin_code = resolve_iata(origin)
    destination_code = resolve_iata(destination)

    if len(origin_code) != 3 or not origin_code.isalpha():
        return {
            "success": False,
            "origin": origin,
            "destination": destination,
            "offers": [],
            "error": (
                f"Invalid origin '{origin}'. Please provide a valid 3-letter uppercase "
                "IATA airport code (e.g., BOM for Mumbai, DEL for Delhi, PNQ for Pune)."
            ),
        }

    if len(destination_code) != 3 or not destination_code.isalpha():
        return {
            "success": False,
            "origin": origin,
            "destination": destination,
            "offers": [],
            "error": (
                f"Invalid destination '{destination}'. Please provide a valid 3-letter uppercase "
                "IATA airport code (e.g., GOI for Goa, BLR for Bangalore, DEL for Delhi)."
            ),
        }

    url = "https://flight-mcp.com/v1/flights/search"

    payload = {
        "origin": origin_code,
        "destination": destination_code,
        "departureDate": departure_date,
        "adults": adults,
        "cabinClass": "economy",
        "currency": "INR",
        "locale": "en-IN",
        "pointOfSaleCountry": "IN",
        "maxResults": 10,
        "cacheTtlSeconds": 300,
    }

    if return_date:
        payload["returnDate"] = return_date

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    response = None

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=20,
        )

        response.raise_for_status()

        data = response.json()

        return format_flight_response(data)

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "origin": origin_code,
            "destination": destination_code,
            "departure_date": departure_date,
            "offers": [],
            "error": "Flight search request timed out. Please try again.",
        }

    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if response is not None:
            try:
                err_data = response.json()
                err_obj = err_data.get("error", {})
                message = err_obj.get("message") or response.text
                details = err_obj.get("details", [])
                if details and isinstance(details, list):
                    detail_texts = [
                        f"{d.get('path')}: {d.get('message')}"
                        for d in details
                        if isinstance(d, dict)
                    ]
                    error_msg = f"{message} ({', '.join(detail_texts)})"
                else:
                    error_msg = message
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