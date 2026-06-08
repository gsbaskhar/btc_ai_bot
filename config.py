import MetaTrader5 as mt5

SYMBOL = "BTCUSD"
TIMEFRAME = mt5.TIMEFRAME_M5

MAGIC = 555777

LOT_SIZE = 0.05

RISK_PERCENT = 1

RISK_REWARD = 2.0

EMA_FAST = 50
EMA_SLOW = 200

RSI_PERIOD = 14
ATR_PERIOD = 14

RSI_BUY = 50
RSI_SELL = 50

MIN_ATR = 100
MAX_ATR = 5000

MAX_SPREAD = 3500

MAX_TRADES_PER_DAY = 5
MAX_DAILY_LOSS = 2

BREAK_EVEN_TRIGGER = 100
TRAILING_TRIGGER = 150
TRAILING_DISTANCE = 100

TRADE_COOLDOWN = 2

ENABLE_AI = False
ENABLE_VOLUME_FILTER = False
ENABLE_HTF_FILTER = False
ENABLE_SESSION_FILTER = False

OPENAI_MODEL = "gpt-4.1-mini"

# Optional MetaTrader 5 terminal path. Set this if MT5 is installed in a non-standard location.
# Example:
# MT5_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"
MT5_PATH = r"C:\Users\Bass\AppData\Roaming\MetaTrader 5\terminal64.exe"

# === Stoploss caps (in points) - adjusted for BTC volatility
MIN_SL_POINTS = 50
MAX_SL_POINTS = 1000