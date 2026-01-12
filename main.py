import asyncio, time, yaml
from core.market_data import get_exchange, get_usdt_pairs, fetch_ohlcv
from core.state_machine import evaluate
from alerts.telegram import send

async def main():
    print("🚀 Bot starting (DEBUG MODE ENABLED)")

    with open("config/settings.yaml") as f:
        cfg = yaml.safe_load(f)

    debug_on = cfg['logic'].get('debug', False)

    exchange = await get_exchange()
    pairs = await get_usdt_pairs(exchange)
    print(f"📊 Watching {len(pairs)} USDT futures pairs")

    last_alert = {}

    while True:
        for symbol in pairs:
            try:
                df15 = await fetch_ohlcv(exchange, symbol, "15m")
                df1h = await fetch_ohlcv(exchange, symbol, "1h")
                df5  = await fetch_ohlcv(exchange, symbol, "5m")

                direction, debug = evaluate(
                    df15, df1h, df5,
                    cfg['logic']['range_lookback']
                )

                if debug_on:
                    print(f"{symbol} | {debug}")

                if direction:
                    now = time.time()
                    cooldown = cfg['logic']['cooldown_minutes'] * 60

                    if symbol not in last_alert or now - last_alert[symbol] > cooldown:
                        msg = f"{symbol} {direction} A+ SCALPING SETUP"
                        print("⚡", msg)
                        if cfg['telegram']['enabled']:
                            send(cfg['telegram']['bot_token'], cfg['telegram']['chat_id'], msg)
                        last_alert[symbol] = now

                await asyncio.sleep(cfg['binance']['rate_limit_delay'])

            except Exception as e:
                print(f"❌ {symbol}: {e}")

        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())