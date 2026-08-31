"""Thin, validated MetaTrader 5 execution adapter."""
import math
import pandas as pd
import MetaTrader5 as mt5

from config import BOT_COMMENT, MAGIC, SLIPPAGE_POINTS, SYMBOL, TIMEFRAME


def initialize_mt5():
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialization failed: {mt5.last_error()}")
    account = mt5.account_info()
    if account is None:
        mt5.shutdown()
        raise RuntimeError("No MT5 account is logged in")
    info = mt5.symbol_info(SYMBOL)
    if info is None:
        mt5.shutdown()
        raise RuntimeError(f"Symbol '{SYMBOL}' was not found in Market Watch")
    if not info.visible and not mt5.symbol_select(SYMBOL, True):
        raise RuntimeError(f"Unable to select symbol '{SYMBOL}'")
    return account


def shutdown_mt5():
    mt5.shutdown()


def get_account_info():
    return mt5.account_info()


def get_tick():
    return mt5.symbol_info_tick(SYMBOL)


def get_symbol_info():
    return mt5.symbol_info(SYMBOL)


def get_positions():
    """Return only positions owned by this bot."""
    positions = mt5.positions_get(symbol=SYMBOL) or ()
    return [p for p in positions if p.magic == MAGIC]


def get_candles(limit=500, closed_only=True):
    # position 0 is the changing candle. Start at 1 for stable signals.
    start_pos = 1 if closed_only else 0
    rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, start_pos, limit)
    if rates is None or len(rates) == 0:
        return None
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df.rename(columns={"tick_volume": "volume"}, inplace=True)
    return df


def spread_points():
    tick, info = get_tick(), get_symbol_info()
    if tick is None or info is None or info.point <= 0:
        return math.inf
    return (tick.ask - tick.bid) / info.point


def _normalize_price(price):
    info = get_symbol_info()
    return round(price, info.digits)


def place_order(direction, volume, sl, tp):
    tick = get_tick()
    info = get_symbol_info()
    if tick is None or info is None:
        return None
    is_buy = direction == "BUY"
    price = tick.ask if is_buy else tick.bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY if is_buy else mt5.ORDER_TYPE_SELL,
        "price": _normalize_price(price),
        "sl": _normalize_price(sl),
        "tp": _normalize_price(tp),
        "deviation": SLIPPAGE_POINTS,
        "magic": MAGIC,
        "comment": BOT_COMMENT,
        "type_time": mt5.ORDER_TIME_GTC,
    }
    # Filling modes differ by broker/symbol.
    check = None
    for filling_mode in (
        mt5.ORDER_FILLING_FOK,
        mt5.ORDER_FILLING_IOC,
        mt5.ORDER_FILLING_RETURN,
    ):
        request["type_filling"] = filling_mode
        check = mt5.order_check(request)
        if check is not None and check.retcode == 0:
            break
    else:
        print(f"Order pre-check failed for every filling mode: {check}")
        return None
    result = mt5.order_send(request)
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order failed: {result}")
        return None
    return result


def modify_position(ticket, sl, tp):
    result = mt5.order_send({
        "action": mt5.TRADE_ACTION_SLTP,
        "position": ticket,
        "sl": _normalize_price(sl),
        "tp": _normalize_price(tp),
    })
    return result is not None and result.retcode == mt5.TRADE_RETCODE_DONE