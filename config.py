"""Single source of truth for the MT5 BTCUSD bot."""
import MetaTrader5 as mt5

# Broker settings: confirm the exact symbol name in your MT5 Market Watch.
SYMBOL = "BTCUSD"
TIMEFRAME = mt5.TIMEFRAME_M5
MAGIC = 555777
BOT_COMMENT = "BTC_MT5_BOT"

# Risk. Start on a demo account and keep this deliberately conservative.
RISK_PERCENT = 0.25
RISK_REWARD = 2.0
MIN_LOT_SIZE = 0.01
MAX_LOT_SIZE = 0.10
MAX_DAILY_LOSS_PERCENT = 2.0
MAX_TRADES_PER_DAY = 3
MAX_CONSECUTIVE_LOSSES = 2
TRADE_COOLDOWN_BARS = 2

# Strategy indicators.
EMA_FAST = 50
EMA_SLOW = 200
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
ATR_PERIOD = 14
ATR_MULTIPLIER = 2.5  # FIXED: Increased from 1.8 to avoid tight stops
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BOLLINGER_PERIOD = 20
MIN_ATR = 30.0
MAX_ATR = 5000.0
MIN_VOLUME_RATIO = 0.9

# Execution. Values ending in _POINTS use the broker's SYMBOL_POINT.
MAX_SPREAD_POINTS = 3500
SLIPPAGE_POINTS = 50

# Exit management uses the original stop distance (1R).
BREAK_EVEN_TRIGGER_R = 1.0
BREAK_EVEN_OFFSET_R = 0.10
TRAILING_TRIGGER_R = 1.5
TRAILING_DISTANCE_R = 1.0
TRAILING_STEP_R = 0.25

# FIXED: Added minimum distance between trades at same price level
MIN_DISTANCE_FROM_LAST_TRADE = 150  # Points

# Optional filters.
ENABLE_SESSION_FILTER = False
ENABLE_HTF_FILTER = True
ENABLE_AI = False
LONDON_START_UTC = 7
LONDON_END_UTC = 10
NY_START_UTC = 13
NY_END_UTC = 17
OPENAI_MODEL = "gpt-4.1-mini"