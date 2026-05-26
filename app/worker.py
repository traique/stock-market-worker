import time
import requests

from supabase_client import supabase


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0"
    )
}


def get_all_symbols():
    symbols = set()

    # holdings
    try:
        holdings_rows = (
            supabase
            .schema("public")
            .table("holdings")
            .select("symbol")
            .execute()
        )

        for row in holdings_rows.data:
            symbol = row.get("symbol")

            if symbol:
                symbols.add(symbol.upper())

    except Exception as e:
        print(f"[HOLDINGS ERROR] {e}")

    # watchlists
    try:
        watchlist_rows = (
            supabase
            .schema("public")
            .table("watchlists")
            .select("symbol")
            .execute()
        )

        for row in watchlist_rows.data:
            symbol = row.get("symbol")

            if symbol:
                symbols.add(symbol.upper())

    except Exception as e:
        print(f"[WATCHLIST ERROR] {e}")

    return list(symbols)


def fetch_price(symbol: str):
    try:
        print(f"[FETCHING] {symbol}")

        url = (
            "https://finance.vietstock.vn/"
            f"{symbol}/overview.htm"
        )

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10,
        )

        if response.status_code != 200:
            print(
                f"[HTTP ERROR] "
                f"{symbol}: "
                f"{response.status_code}"
            )

            return None

        html = response.text

        marker = 'Price:'

        if marker not in html:
            print(
                f"[NO PRICE MARKER] "
                f"{symbol}"
            )

            return None

        # debug ngắn
        index = html.find(marker)

        snippet = html[
            index:index + 200
        ]

        print(
            f"[HTML SNIPPET] "
            f"{symbol}"
        )

        print(snippet)

        return None

    except Exception as e:
        print(
            f"[FETCH ERROR] "
            f"{symbol}: {str(e)}"
        )

        return None


def update_market_price(data):
    try:
        (
            supabase
            .schema("public")
            .table("market_prices")
            .upsert({
                "symbol": data["symbol"],
                "price": data["price"],
                "volume": data["volume"],
            })
            .execute()
        )

        print(
            f"[UPDATED] "
            f"{data['symbol']} "
            f"{data['price']}"
        )

    except Exception as e:
        print(
            f"[SUPABASE ERROR] "
            f"{data['symbol']}: {e}"
        )


def update_prices():
    print("Updating market prices...")

    symbol = "SHS"

    data = fetch_price(symbol)

    print(f"[DEBUG RESULT] {data}")

    print("Update completed.")
