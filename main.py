"""Run the conservative MT5 BTCUSD bot.

Use a demo account first. This program can submit live market orders.
"""
import time
from datetime import datetime, timezone

import MetaTrader5 as mt5

import config
from indicators import add_all_indicators
from logger import get_initial_stop, initialize_log, log_order, sync_closed_deals
from mt5_connector import (
    get_account_info, get_candles, get_positions, get_symbol_info, get_tick,
    initialize_mt5, modify_position, place_order, shutdown_mt5, spread_points,
)
from multi_timeframe import get_htf_trend
from risk_manager import calculate_position_size, calculate_sl_tp, trading_allowed
from session_filter import session_ok
from strategy.enhanced_strategy import get_breakout_signal, get_trend


def manage_positions():
    """Manage exits from the original per-trade risk (R), not fixed points."""
    info, tick = get_symbol_info(), get_tick()
    if info is None or tick is None:
        return
    point = info.point
    min_distance = max(info.trade_stops_level, info.trade_freeze_level) * point
    for position in get_positions():
        is_buy = position.type == mt5.POSITION_TYPE_BUY
        market_price = tick.bid if is_buy else tick.ask
        initial_sl = get_initial_stop(position.ticket)
        risk_distance = abs(position.price_open - initial_sl) if initial_sl else 0.0
        if risk_distance <= 0:
            print(f"No initial SL recorded for #{position.ticket}; trailing skipped")
            continue
        gain = (market_price - position.price_open) if is_buy else (position.price_open - market_price)
        candidate = None
        if gain >= risk_distance * config.BREAK_EVEN_TRIGGER_R:
            candidate = position.price_open + (risk_distance * config.BREAK_EVEN_OFFSET_R if is_buy else -risk_distance * config.BREAK_EVEN_OFFSET_R)
        if gain >= risk_distance * config.TRAILING_TRIGGER_R:
            trailing = market_price - risk_distance * config.TRAILING_DISTANCE_R if is_buy else market_price + risk_distance * config.TRAILING_DISTANCE_R
            candidate = max(candidate or trailing, trailing) if is_buy else min(candidate or trailing, trailing)
        if candidate is None:
            continue
        # Never loosen SL and do not send a stop inside the broker's stop/freeze zone.
        if is_buy:
            candidate = min(candidate, market_price - min_distance)
            better = position.sl == 0.0 or candidate > position.sl + risk_distance * config.TRAILING_STEP_R
        else:
            candidate = max(candidate, market_price + min_distance)
            better = position.sl == 0.0 or candidate < position.sl - risk_distance * config.TRAILING_STEP_R
        if better and modify_position(position.ticket, candidate, position.tp):
            print(f"Trailing stop moved for #{position.ticket} to {candidate:.{info.digits}f}")


def can_trade(df):
    if config.ENABLE_SESSION_FILTER and not session_ok():
        return False, "outside UTC trading session"
    if spread_points() > config.MAX_SPREAD_POINTS:
        return False, "spread above limit"
    atr = df.atr.iloc[-1]
    if not config.MIN_ATR <= atr <= config.MAX_ATR:
        return False, f"ATR outside range ({atr:.2f})"
    allowed, reason = trading_allowed()
    if not allowed:
        return False, reason
    return True, ""


def run():
    account = initialize_mt5()
    initialize_log()
    print(f"MT5 bot ready | account={account.login} | symbol={config.SYMBOL} | balance={account.balance:.2f}")
    last_bar_time = None
    last_trade_bar = -999
    bar_number = 0

    while True:
        try:
            closed_pnls = sync_closed_deals()
            for pnl in closed_pnls:
                print(f"Closed bot deal logged: net P/L {pnl:.2f}")
            manage_positions()

            df = get_candles(500, closed_only=True)
            if df is None or len(df) < 250:
                print("Waiting for sufficient closed candles...")
                time.sleep(5)
                continue
            df = add_all_indicators(df)
            bar_time = df.time.iloc[-1]
            if bar_time == last_bar_time:
                time.sleep(2)
                continue
            last_bar_time = bar_time
            bar_number += 1

            # One bot position at a time; manual positions are ignored.
            if get_positions():
                print(f"{bar_time}: bot position open; entries paused")
                continue
            allowed, reason = can_trade(df)
            if not allowed:
                print(f"{bar_time}: no trade — {reason}")
                continue
            if bar_number - last_trade_bar < config.TRADE_COOLDOWN_BARS:
                print(f"{bar_time}: no trade — cooldown")
                continue

            trend = get_trend(df)
            if trend == "SIDEWAYS":
                print(f"{bar_time}: no trade — sideways")
                continue
            if config.ENABLE_HTF_FILTER and get_htf_trend(config.SYMBOL) != trend:
                print(f"{bar_time}: no trade — H1 trend conflict")
                continue
            if config.ENABLE_AI:
                from ai_filter import ask_ai
                result = ask_ai(df)
                if not result or result.get("market") != "TRENDING":
                    print(f"{bar_time}: no trade — AI filter")
                    continue

            signal = get_breakout_signal(df, trend, debug=True)
            if signal is None:
                print(f"{bar_time}: no qualified signal")
                continue
            tick = get_tick()
            if tick is None:
                continue
            entry = tick.ask if signal == "BUY" else tick.bid
            sl, tp = calculate_sl_tp(signal, entry, df.atr.iloc[-1])
            volume = calculate_position_size(entry, sl)
            result = place_order(signal, volume, sl, tp)
            if result:
                log_order(result, signal, volume, sl, tp)
                last_trade_bar = bar_number
                print(f"Opened {signal} #{result.order}: {volume} lots at {result.price}")
        except KeyboardInterrupt:
            print("Bot stopped by user.")
            break
        except Exception as exc:
            print(f"Loop error: {exc}")
            time.sleep(10)
    shutdown_mt5()


if __name__ == "__main__":
    run()
