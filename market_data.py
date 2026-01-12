import ccxt.async_support as ccxt
import pandas as pd

async def get_exchange():
    exchange = ccxt.binance({
        "options": {"defaultType": "future"},
        "enableRateLimit": True
    })
    await exchange.load_markets()
    return exchange

async def get_usdt_pairs(exchange):
    pairs = []
    for symbol, market in exchange.markets.items():
        if (
            market.get("quote") == "USDT"
            and market.get("linear") is True
            and market.get("swap") is True
            and market.get("active") is True
        ):
            pairs.append(symbol)
    return pairs

async def fetch_ohlcv(exchange, symbol, timeframe, limit=100):
    data = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(data, columns=["time","open","high","low","close","volume"])
    return df