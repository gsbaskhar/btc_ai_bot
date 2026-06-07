import time
from datetime import datetime

from config import *

from mt5_connector import *
from data_handler import *
from indicators import *

from strategy.trend_strategy import *
from strategy.breakout_strategy import *
from strategy.liquidity_strategy import *

from risk_manager import *
from trade_manager import *

from logger import *

from ai_filter import *
from session_filter import *
from multi_timeframe import *

# ===================================
# VARIABLES
# ===================================

last_bar = None

candle_counter = 0

last_trade_candle = -100

daily_trade_count = 0

current_day = None

# ===================================
# INIT
# ===================================

initialize_mt5()

initialize_log()

# ===================================
# MAIN LOOP
# ===================================

while True:

    try:

        today = datetime.now().date()

        if current_day != today:

            current_day = today

            daily_trade_count = 0

            print("NEW DAY - TRADE COUNT RESET")

        df = get_candles()

        if df is None:

            time.sleep(5)

            continue

        df = add_all_indicators(df)

        current_time = df.iloc[-1]["time"]

        positions = get_positions()

        if positions:

            tick = get_tick()

            apply_break_even(
                positions,
                tick
            )

            apply_trailing_stop(
                positions,
                tick
            )

            time.sleep(5)

            continue

        if last_bar is None or current_time > last_bar:

            last_bar = current_time

            candle_counter += 1

            print("\n" + "=" * 60)
            print(f"CANDLE : {candle_counter}")
            print(f"TIME   : {current_time}")
            print("=" * 60)

            tick = get_tick()

            symbol_info = get_symbol_info()

            if not spread_ok(
                tick,
                symbol_info
            ):

                print("SPREAD TOO HIGH")

                continue

            if not volatility_ok(df):

                print("LOW VOLATILITY")

                continue

            trend = get_trend(df)

            print(f"TREND : {trend}")

            if trend == "SIDEWAYS":

                print("SIDEWAYS MARKET")

                continue

            if not session_ok():

                print("BAD SESSION")

                continue

            htf_trend = get_htf_trend(SYMBOL)

            print(f"HTF TREND : {htf_trend}")

            if trend != htf_trend:

                print("HTF CONFLICT")

                continue

            if ENABLE_AI:

                ai_result = ask_ai(df)

                print(ai_result)

                if ai_result:

                    if ai_result["market"] == "RANGING":

                        print("AI BLOCKED TRADE")

                        continue

            if (
                candle_counter
                - last_trade_candle
                < TRADE_COOLDOWN
            ):

                print("COOLDOWN ACTIVE")

                continue

            signal = get_breakout_signal(
                df,
                trend
            )

            print(f"SIGNAL : {signal}")

            if signal is None:

                continue

            entry = (
                tick.ask
                if signal == "BUY"
                else tick.bid
            )

            atr = df["atr"].iloc[-1]

            sl, tp = calculate_sl_tp(
                signal,
                entry,
                atr
            )

            print(f"ENTRY : {entry}")
            print(f"SL    : {sl}")
            print(f"TP    : {tp}")

            if daily_trade_count >= MAX_TRADES_PER_DAY:

                print(
                    f"MAX DAILY TRADES REACHED "
                    f"({MAX_TRADES_PER_DAY})"
                )

                continue

            result = place_order(
                signal,
                LOT_SIZE,
                sl,
                tp
            )

            print(result)

            if result and result.retcode == 10009:

                daily_trade_count += 1

                print(
                    f"TRADE OPENED "
                    f"({daily_trade_count}/{MAX_TRADES_PER_DAY})"
                )

                last_trade_candle = candle_counter

            else:

                print("ORDER FAILED")

        time.sleep(5)

    except KeyboardInterrupt:

        print("BOT STOPPED")

        shutdown_mt5()

        break

    except Exception as e:

        print(f"ERROR : {e}")

        time.sleep(10)