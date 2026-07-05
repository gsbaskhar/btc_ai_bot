# main.py
import time
from datetime import datetime
import sys
import os

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import config first
import config

# Then import from mt5_connector (which uses config)
from mt5_connector import *
from indicators import add_all_indicators
from strategy.enhanced_strategy import get_trend, get_breakout_signal, get_liquidity_signal
from risk_manager import *
from logger import *
from ai_filter import ask_ai
from session_filter import session_ok
from multi_timeframe import get_htf_trend

# Get config variables
SYMBOL = config.SYMBOL
TIMEFRAME = config.TIMEFRAME
MAGIC = config.MAGIC
MAX_TRADES_PER_DAY = config.MAX_TRADES_PER_DAY
TRADE_COOLDOWN = config.TRADE_COOLDOWN
TRAILING_TRIGGER = config.TRAILING_TRIGGER
TRAILING_DISTANCE = config.TRAILING_DISTANCE
MIN_ATR = config.MIN_ATR
ENABLE_SESSION_FILTER = config.ENABLE_SESSION_FILTER
ENABLE_HTF_FILTER = config.ENABLE_HTF_FILTER
ENABLE_AI = config.ENABLE_AI
MAX_CONSECUTIVE_LOSSES = config.MAX_CONSECUTIVE_LOSSES

# ===================================
# VARIABLES
# ===================================

last_bar = None
candle_counter = 0
last_trade_candle = -100
daily_trade_count = 0
current_day = None
consecutive_losses = 0
total_trades = 0
winning_trades = 0
losing_trades = 0

# ===================================
# INITIALIZE
# ===================================

print("🤖 BTC AI TRADING BOT")
print("=" * 60)

# Connect to MT5
try:
    initialize_mt5()
except Exception as e:
    print(f"❌ Failed to initialize MT5: {e}")
    sys.exit(1)

# Initialize log
initialize_log()

# Check if account is healthy
account = get_account_info()
if account is None:
    print("❌ No account info")
    sys.exit(1)

print(f"\n📊 ACCOUNT SUMMARY")
print(f"💰 Balance: ${account.balance:.2f}")
print(f"📈 Equity: ${account.equity:.2f}")
print(f"📉 Free Margin: ${account.margin_free:.2f}")
print(f"📊 Leverage: {account.leverage}x")
print("=" * 60)

# ===================================
# MAIN LOOP
# ===================================

print("\n🚀 STARTING TRADING LOOP...\n")

while True:
    
    try:
        today = datetime.now().date()
        
        # Reset daily counters
        if current_day != today:
            current_day = today
            daily_trade_count = 0
            consecutive_losses = 0
            print("\n" + "=" * 60)
            print(f"📅 NEW DAY: {today}")
            print("=" * 60)
        
        # Get candle data
        df = get_candles(500)
        if df is None or len(df) < 100:
            print("⏳ Waiting for candles...")
            time.sleep(5)
            continue
        
        # Add indicators
        df = add_all_indicators(df)
        current_time = df.iloc[-1]["time"]
        
        # Check for existing positions
        positions = get_positions()
        if positions and len(positions) > 0:
            # Manage existing positions (trailing stop)
            for pos in positions:
                tick = get_tick()
                if tick is None:
                    continue
                    
                # Calculate current profit
                if pos.type == 0:  # BUY
                    current_profit = (tick.bid - pos.price_open) * pos.volume
                    entry_price = pos.price_open
                    current_price = tick.bid
                else:  # SELL
                    current_profit = (pos.price_open - tick.ask) * pos.volume
                    entry_price = pos.price_open
                    current_price = tick.ask
                
                # Check for trailing stop
                if pos.profit > TRAILING_TRIGGER:
                    new_sl = entry_price + (pos.profit / pos.volume) - TRAILING_DISTANCE
                    if pos.type == 0:  # BUY
                        new_sl = current_price - TRAILING_DISTANCE
                    else:  # SELL
                        new_sl = current_price + TRAILING_DISTANCE
                    
                    # Update SL
                    if new_sl != pos.sl:
                        print(f"📉 Trailing SL updated to {new_sl:.2f}")
                        modify_position(pos.ticket, new_sl, pos.tp)
            
            time.sleep(5)
            continue
        
        # New candle check
        if last_bar is None or current_time > last_bar:
            last_bar = current_time
            candle_counter += 1
            
            print("\n" + "=" * 60)
            print(f"🕐 CANDLE : {candle_counter}")
            print(f"📅 TIME   : {current_time}")
            print(f"💰 CLOSE  : {df.iloc[-1]['close']:.2f}")
            print("=" * 60)
            
            # Check session filter
            if ENABLE_SESSION_FILTER:
                if not session_ok():
                    print("⏰ OUTSIDE TRADING HOURS")
                    time.sleep(5)
                    continue
            
            # Check volatility
            atr = df["atr"].iloc[-1]
            if atr < MIN_ATR:
                print(f"📊 LOW VOLATILITY: ATR={atr:.2f}")
                time.sleep(5)
                continue
            
            # Check max trades per day
            if daily_trade_count >= MAX_TRADES_PER_DAY:
                print(f"📊 MAX TRADES REACHED: {daily_trade_count}")
                time.sleep(5)
                continue
            
            # Check daily loss limit
            if check_daily_loss():
                print("⚠️ DAILY LOSS LIMIT REACHED - STOPPING")
                time.sleep(60)
                continue
            
            # Check consecutive losses
            if check_consecutive_losses():
                print("⚠️ MAX CONSECUTIVE LOSSES - COOLDOWN")
                time.sleep(60)
                continue
            
            # Get market trend
            trend = get_trend(df)
            print(f"📊 TREND : {trend}")
            
            if trend == "SIDEWAYS":
                print("⏳ SIDEWAYS MARKET - WAITING")
                time.sleep(5)
                continue
            
            # HTF filter (only if enabled)
            if ENABLE_HTF_FILTER:
                try:
                    htf_trend = get_htf_trend(SYMBOL)
                    print(f"📈 HTF TREND : {htf_trend}")
                    if trend != htf_trend:
                        print("❌ HTF CONFLICT - SKIPPING")
                        time.sleep(5)
                        continue
                except Exception as e:
                    print(f"⚠️ HTF Filter error: {e}")
            
            # AI filter (only if enabled)
            if ENABLE_AI:
                try:
                    ai_result = ask_ai(df)
                    if ai_result and ai_result.get("market") == "RANGING":
                        print("🤖 AI BLOCKED TRADE (RANGING)")
                        time.sleep(5)
                        continue
                except Exception as e:
                    print(f"⚠️ AI Filter error: {e}")
            
            # Cooldown
            if candle_counter - last_trade_candle < TRADE_COOLDOWN:
                print(f"⏳ COOLDOWN: {candle_counter - last_trade_candle}/{TRADE_COOLDOWN}")
                time.sleep(5)
                continue
            
            # Get trading signal
            signal = get_breakout_signal(df, trend, debug=True)
            
            if signal is None:
                # Try liquidity strategy as secondary
                signal = get_liquidity_signal(df)
            
            if signal is None:
                print("⏳ NO SIGNAL")
                time.sleep(5)
                continue
            
            # Calculate entry, SL, TP
            tick = get_tick()
            if tick is None:
                continue
            
            entry = tick.ask if signal == "BUY" else tick.bid
            sl, tp = calculate_sl_tp(signal, entry, atr)
            
            # Calculate position size
            lot_size = calculate_position_size(entry, atr)
            
            print("\n" + "=" * 60)
            print(f"🎯 TRADE SIGNAL: {signal}")
            print(f"💰 ENTRY: {entry:.2f}")
            print(f"📉 SL: {sl:.2f}")
            print(f"📈 TP: {tp:.2f}")
            print(f"📊 LOT SIZE: {lot_size:.2f}")
            print("=" * 60)
            
            # Place order
            result = place_order(signal, lot_size, sl, tp)
            
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                daily_trade_count += 1
                total_trades += 1
                last_trade_candle = candle_counter
                
                print("\n✅ TRADE OPENED SUCCESSFULLY!")
                print(f"📊 Ticket: {result.order}")
                print(f"📈 Daily Trades: {daily_trade_count}/{MAX_TRADES_PER_DAY}")
                
                # Log trade
                log_trade([
                    current_time,
                    signal,
                    entry,
                    sl,
                    tp,
                    0
                ])
            else:
                print("❌ ORDER FAILED")
        
        time.sleep(2)
        
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("🛑 BOT STOPPED BY USER")
        print("=" * 60)
        print(f"\n📊 TRADING SUMMARY")
        print(f"Total Trades: {total_trades}")
        if total_trades > 0:
            winrate = (winning_trades / total_trades) * 100
            print(f"Win Rate: {winrate:.2f}%")
        shutdown_mt5()
        break
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(10)