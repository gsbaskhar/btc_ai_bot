# BTCUSD MT5 Bot

An MT5-only, closed-candle BTCUSD M5 trend-breakout bot. It is designed to be
auditable and conservative; it is **not** a guarantee of profit.

## Before running

1. Use a demo account and log in through the installed MetaTrader 5 terminal.
2. Confirm your broker's exact BTC symbol in Market Watch and set `SYMBOL` in
   `config.py` (common alternatives are `BTCUSDm` and `BTCUSD.a`).
3. Review `RISK_PERCENT`, volume limits, spread limit, and UTC session settings
   in `config.py` for your broker's contract specification.
4. Install dependencies: `pip install -r requirements.txt`.
5. Run the connection check: `python test_mt5.py`.
6. Start only after the above succeeds: `python main.py`.

## Safety controls

- Uses only completed M5 candles (never the currently forming candle).
- Opens/manages only positions matching this bot's MT5 magic number.
- Enforces spread, daily entry count, daily loss, and consecutive-loss limits.
- Sizes risk from the broker-reported tick size/value and respects volume limits.
- Uses append-only `logs/orders.csv` and `logs/closed_deals.csv` audit logs.

## Backtesting

Provide a CSV with `time,open,high,low,close,volume` columns:

`python backtester.py path/to/history.csv`

The backtest reports price points, not account-currency P/L, because accurate
currency P/L depends on the broker's historical contract/tick specification and
costs. Include spread, commissions, swaps, and slippage before trusting results.
