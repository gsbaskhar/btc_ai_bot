import MetaTrader5 as mt5

from config import *

# ======== SPREAD CHECK ============

def spread_ok(tick, symbol_info):

    spread = (
        tick.ask - tick.bid
    ) / symbol_info.point

    print(f"SPREAD : {spread:.0f}")

    return spread <= MAX_SPREAD


# =========== VOLATILITY CHECK =============

def volatility_ok(df):

    atr = df['atr'].iloc[-1]

    print(f"ATR : {atr:.2f}")

    if atr < MIN_ATR:
        return False

    if atr > MAX_ATR:
        return False

    return True


# ========== SL TP CALCULATION ===============

def calculate_sl_tp(direction, entry, atr):
    # ATR based stop (price units)
    sl_distance = atr * 1.5

    # attempt to get symbol point to convert to points
    try:
        symbol = mt5.symbol_info(SYMBOL)
        point = symbol.point if symbol is not None else None
    except Exception:
        symbol = None
        point = None

    # if we have point information, clamp SL in points to keep losses small
    if point and point > 0:
        sl_points = sl_distance / point

        # clamp SL to configured min/max points (small single-digit loss)
        sl_points = max(MIN_SL_POINTS, min(sl_points, MAX_SL_POINTS))

        sl_price_dist = sl_points * point

    else:
        # fallback to price-based clamps (legacy)
        sl_price_dist = max(min(sl_distance, 2000), 150)

    if direction == "BUY":
        sl = entry - sl_price_dist
        tp = entry + (sl_price_dist * RISK_REWARD)
    else:
        sl = entry + sl_price_dist
        tp = entry - (sl_price_dist * RISK_REWARD)

    return sl, tp