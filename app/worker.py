import time
import requests

from supabase_client import supabase


VCI_URL = (
    "https://priceboard-api.vcbs.com.vn/"
    "stock/snapshot"
)


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

        response = requests.get(
            f"{VCI_URL}/{symbol}",
            timeout=10,
        )

        if response.status_code != 200:
            print(
                f"[HTTP ERROR] "
                f"{symbol}: "
                f"{response.status_code}"
            )

            return None

        data = response.json()

        print(f"[RAW DATA] {symbol}")
        print(data)

        price = (
            data.get("matchPrice")
            or data.get("lastPrice")
            or 0
        )

        volume = (
            data.get("matchVol")
            or data.get("totalVol")
            or 0
        )

        if not price:
            print(f"[INVALID PRICE] {symbol}")
            return None

        return {
            "symbol": symbol,
            "price": float(price),
            "volume": float(volume),
        }

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

    symbols = get_all_symbols()

    print(f"Found {len(symbols)} symbols")

    if not symbols:
        print("No symbols found")
        return

    for symbol in symbols:
        data = fetch_price(symbol)

        if data:
            update_market_price(data)

        time.sleep(0.5)

    print("Update completed.")
