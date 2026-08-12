"""Risk and broker-aware sizing helpers for MetaTrader 5."""
from datetime import datetime, timezone

import MetaTrader5 as mt5

from config import *
from logger import daily_order_count


def _symbol_info():
    info = mt5.symbol_info(SYMBOL)
    if info is None:
        raise RuntimeError(f"Symbol unavailable: {SYMBOL}")
    return info


def _round_volume(volume, info):
    step = info.volume_step or MIN_LOT_SIZE
    lower = max(MIN_LOT_SIZE, info.volume_min)
    upper = min(MAX_LOT_SIZE, info.volume_max)
    volume = max(lower, min(upper, volume))
    steps = round(volume / step)
    return round(max(lower, min(upper, steps * step)), 8)


def calculate_position_size(entry, stop_loss):
    """Return volume whose estimated loss at SL is RISK_PERCENT of balance.

    MT5 tick value/tick size are broker supplied, so this works across BTCUSD
    contract specifications instead of assuming a fixed BTC contract size.
    """
    account = mt5.account_info()
    info = _symbol_info()
    if account is None or info.trade_tick_size <= 0 or info.trade_tick_value <= 0:
        return _round_volume(MIN_LOT_SIZE, info)

    stop_distance = abs(entry - stop_loss)
    loss_per_lot = (stop_distance / info.trade_tick_size) * info.trade_tick_value
    if loss_per_lot <= 0:
        return _round_volume(MIN_LOT_SIZE, info)

    risk_amount = account.balance * (RISK_PERCENT / 100.0)
    volume = _round_volume(risk_amount / loss_per_lot, info)
    return volume


def calculate_sl_tp(signal, entry, atr, enforce_broker_minimum=True):
    distance = max(float(atr) * ATR_MULTIPLIER, 1.0)
    if enforce_broker_minimum:
        info = _symbol_info()
        # MT5 rejects stops closer than the symbol's broker-defined stop level.
        distance = max(distance, max(info.trade_stops_level, info.trade_freeze_level) * info.point)
    if signal == "BUY":
        return entry - distance, entry + distance * RISK_REWARD
    return entry + distance, entry - distance * RISK_REWARD


def _today_deals():
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return mt5.history_deals_get(start, now) or ()


def _bot_deals():
    return [d for d in _today_deals() if d.symbol == SYMBOL and d.magic == MAGIC]


def daily_entry_count():
    return daily_order_count()


def daily_loss_percent():
    account = mt5.account_info()
    if account is None or account.balance <= 0:
        return 0.0
    closed_pnl = sum(
        d.profit + d.swap + d.commission
        for d in _bot_deals()
        if d.entry in (mt5.DEAL_ENTRY_OUT, mt5.DEAL_ENTRY_OUT_BY)
    )
    return max(0.0, -closed_pnl / account.balance * 100.0)


def consecutive_losses():
    exits = [d for d in _bot_deals() if d.entry in (mt5.DEAL_ENTRY_OUT, mt5.DEAL_ENTRY_OUT_BY)]
    exits.sort(key=lambda d: getattr(d, "time_msc", 0), reverse=True)
    count = 0
    for deal in exits:
        if deal.profit + deal.swap + deal.commission < 0:
            count += 1
        else:
            break
    return count


def trading_allowed():
    if daily_entry_count() >= MAX_TRADES_PER_DAY:
        return False, "daily trade limit reached"
    if daily_loss_percent() >= MAX_DAILY_LOSS_PERCENT:
        return False, "daily loss limit reached"
    if consecutive_losses() >= MAX_CONSECUTIVE_LOSSES:
        return False, "consecutive-loss limit reached"
    return True, ""
