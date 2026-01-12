from core.indicators import ema, rsi, volume_spike

def liquidity_sweep(df, direction, lookback):
    hi = df['high'][-lookback:].max()
    lo = df['low'][-lookback:].min()
    last = df.iloc[-1]

    if direction == "LONG":
        return last['low'] < lo and last['close'] > lo
    if direction == "SHORT":
        return last['high'] > hi and last['close'] < hi
    return False

def decide_15m(df):
    price = df['close'].iloc[-1]
    ema50 = ema(df['close'], 50).iloc[-1]
    rsi14 = rsi(df['close'], 14).iloc[-1]

    if price > ema50 and rsi14 > 50:
        return "LONG", f"price>EMA50 & RSI={round(rsi14,1)}"
    if price < ema50 and rsi14 < 50:
        return "SHORT", f"price<EMA50 & RSI={round(rsi14,1)}"
    return None, "no bias"

def confirm_1h(df, direction):
    ema50 = ema(df['close'], 50).iloc[-1]
    ema200 = ema(df['close'], 200).iloc[-1]
    ok = ema50 > ema200 if direction == "LONG" else ema50 < ema200
    return ok, f"EMA50={round(ema50,2)} EMA200={round(ema200,2)}"

def entry_5m(df):
    price = df['close'].iloc[-1]
    ema9 = ema(df['close'], 9).iloc[-1]
    ema21 = ema(df['close'], 21).iloc[-1]
    vol = volume_spike(df['volume'], 10)

    ok = min(ema9, ema21) <= price <= max(ema9, ema21) and vol
    return ok, f"price in EMA9-21 & volume={vol}"

def evaluate(df15, df1h, df5, lookback):
    debug = {}

    direction, debug['bias'] = decide_15m(df15)
    if not direction:
        return None, debug

    ok, debug['confirm'] = confirm_1h(df1h, direction)
    if not ok:
        return None, debug

    sweep = liquidity_sweep(df15, direction, lookback)
    debug['sweep'] = sweep
    if not sweep:
        return None, debug

    ok, debug['entry'] = entry_5m(df5)
    if not ok:
        return None, debug

    return direction, debug