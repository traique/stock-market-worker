from vnstock.api.quote import Quote

from supabase_client import supabase

WATCHLIST = [
    "SHS",
    "FPT",
    "HPG",
    "BSR",
    "VCB",
    "SSI",
]

def fetch_price(symbol: str):
    try:
        q = Quote(
            symbol=symbol,
            source="VCI",
        )

        df = q.intraday()

        if df.empty:
            print(f"[EMPTY] {symbol}")
            return None

        latest = df.iloc[-1]

        price = latest.get("price")
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


def update_prices():
    print("Updating market prices...")

    for symbol in WATCHLIST:
        data = fetch_price(symbol)

        if not data:
            continue

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
                f"{symbol}: {e}"
            )

    print("Update completed.")
