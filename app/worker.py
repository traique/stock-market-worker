import time

from vnstock.api.quote import Quote

from supabase_client import supabase


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

        q = Quote(
            symbol=symbol,
            source="VCI",
        )

        df = q.history(
            period="1D",
            interval="1m",
        )

        if df is None:
            print(f"[NONE] {symbol}")
            return None

        if len(df) == 0:
            print(f"[EMPTY] {symbol}")
            return None

        latest = df.iloc[-1]

        price = latest.get("close")
        volume = latest.get("volume", 0)

        if not price:
            print(f"[INVALID PRICE] {symbol}")
            return None

        return {
            "symbol": symbol,
            "price": float(price),
            "volume": float(volume or 0),
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

        # tránh rate limit
        time.sleep(1)

    print("Update completed.")
