from vnstock import Vnstock
from supabase_client import supabase

WATCHLIST = [
    "SHS",
    "FPT",
    "HPG",
    "BSR",
]

def fetch_price(symbol: str):
    try:
        stock = Vnstock().stock(
            symbol=symbol,
            source='VCI',
        )

        df = stock.quote.intraday()

        if df.empty:
            return None

        latest = df.iloc[-1]

        return {
            "symbol": symbol,
            "price": float(latest["price"]),
            "volume": float(latest["volume"]),
        }

    except Exception as e:
        print(f"[ERROR] {symbol}: {e}")
        return None


def update_prices():
    for symbol in WATCHLIST:
        data = fetch_price(symbol)

        if not data:
            continue

        supabase.table("market_prices").upsert({
            "symbol": data["symbol"],
            "price": data["price"],
            "volume": data["volume"],
        }).execute()

        print(f"Updated {symbol}")
