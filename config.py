# config.py
import MetaTrader5 as mt5

# ============================================
# TRADING SYMBOL & TIMEFRAME
# ============================================
SYMBOL = "BTCUSD"
TIMEFRAME = mt5.TIMEFRAME_M5
MAGIC = 555777

# ============================================
# POSITION SIZING
# ============================================
LOT_SIZE = 0.02
MAX_LOT_SIZE = 0.10  # UNCOMMENTED
MIN_LOT_SIZE = 0.01  # UNCOMMENTED

# ============================================
# RISK MANAGEMENT
# ============================================
RISK_PERCENT = 1.0  # Reduced from 1.5
RISK_REWARD = 3.0   # Increased from 2.5
MAX_DAILY_LOSS = 2  # Reduced from 3
MAX_TRADES_PER_DAY = 3  # Reduced from 5
MAX_CONSECUTIVE_LOSSES = 2  # Reduced from 3

# ============================================
# INDICATOR SETTINGS
# ============================================
EMA_FAST = 20
EMA_MEDIUM = 50
EMA_SLOW = 200
RSI_PERIOD = 14
RSI_OVERBOUGHT = 75  # Increased
RSI_OVERSOLD = 25    # Decreased
ATR_PERIOD = 14
ATR_MULTIPLIER = 1.8  # Increased
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2

# ============================================
# FILTERS
# ============================================
MIN_ATR = 30  # Reduced
MAX_ATR = 5000
MAX_SPREAD = 3500
MIN_VOLUME_RATIO = 0.8
TRADE_COOLDOWN = 2

# ============================================
# EXIT CONDITIONS
# ============================================
BREAK_EVEN_TRIGGER = 30  # Reduced
TRAILING_TRIGGER = 60   # Reduced
TRAILING_DISTANCE = 30  # Reduced

# ============================================
# FILTER SWITCHES
# ============================================
ENABLE_AI = False
ENABLE_HTF_FILTER = False
ENABLE_SESSION_FILTER = False  # Trade anytime
ENABLE_VOLUME_FILTER = False

# ============================================
# AI SETTINGS
# ============================================
OPENAI_MODEL = "gpt-4.1-mini"

# ============================================
# SESSION TIMES (London & NY)
# ============================================
LONDON_START = 7
LONDON_END = 10
NY_START = 13
NY_END = 17