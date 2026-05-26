import time

from vnstock.api.quote import Quote

from supabase_client import supabase


def get_all_symbols():
    symbols = set()

    # portfolios
    try:
        portfolio_rows = (
            supabase.table("portfolios")
            .select("symbol")
            .execute()
        )

        for row in portfolio_rows.data:
            symbol = row.get("symbol")

            if symbol:
                symbols.add(symbol.upper())

    except Exception as e:
        print(f"[PORTFOLIO ERROR] {e}")

    # watchlists
    try:
        watchlist_rows = (
            supabase.table("watchlists")
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
        q = Quote(
            symbol=symbol,
            source="VCI",
        )

        df = q.history(
            period="1D",
            interval="1m",
        )

        if df.empty:
            print(f"[EMPTY] {symbol}")
            return None

        latest = df.iloc[-1]

        price = latest.get("close")
        volume = latest.get("volume")

        if price is None:
            print(f"[NO PRICE] {symbol}")
            return None

        return {
            "symbol": symbol,
            "price": float(price),
            "volume": float(volume or 0),
        }

    except Exception as e:
        print(f"[ERROR] {symbol}: {e}")
        return None


def update_market_price(data):
    try:
        supabase.table(
            "market_prices"
        ).upsert({
            "symbol": data["symbol"],
            "price": data["price"],
            "volume": data["volume"],
        }).execute()

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

        if not data:
            continue

        update_market_price(data)

        # tránh rate limit
        time.sleep(3)

    print("Update completed.")
