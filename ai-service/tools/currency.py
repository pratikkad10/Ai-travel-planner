from langchain.tools import tool
import requests

@tool
def fetch_currency_exchange_rate(
    base_currency: str,
    target_currency: str
) -> float:
    """
    Fetch the latest exchange rate between two currencies.

    Args:
        base_currency: Three-letter currency code, e.g. USD.
        target_currency: Three-letter currency code, e.g. INR.

    Returns:
        Exchange rate from base_currency to target_currency.
    """

    base_currency = base_currency.strip().upper()
    target_currency = target_currency.strip().upper()

    if len(base_currency) != 3 or len(target_currency) != 3:
        raise ValueError(
            "Currency codes must be 3 letters, e.g. USD, EUR, INR."
        )

    if base_currency == target_currency:
        return 1.0

    url = f"https://open.er-api.com/v6/latest/{base_currency}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("result") != "success":
            raise RuntimeError(
                f"Currency API returned an error: {data}"
            )

        rates = data.get("rates", {})

        rate = rates.get(target_currency)

        if rate is None:
            raise ValueError(
                f"Currency not supported: {target_currency}"
            )

        return float(rate)

    except requests.exceptions.Timeout as e:
        raise RuntimeError(
            "Currency API request timed out."
        ) from e

    except requests.exceptions.RequestException as e:
        raise RuntimeError(
            f"Currency API request failed: {e}"
        )


# result = fetch_currency_exchange_rate.invoke({
#     "base_currency": "USD",
#     "target_currency": "INR"
# })

# print(result)
