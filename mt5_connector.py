# mt5_connector.py
import MetaTrader5 as mt5
import time
import pandas as pd
import sys
import os

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import config - BUT DON'T import from mt5_connector in config.py
import config

# Get variables from config
SYMBOL = config.SYMBOL
TIMEFRAME = config.TIMEFRAME
MAGIC = config.MAGIC

print("=" * 60)
print("📊 MT5 CONNECTOR INITIALIZED")
print(f"✅ Symbol: {SYMBOL}")
print(f"✅ Timeframe: {TIMEFRAME}")
print(f"✅ Magic: {MAGIC}")
print("=" * 60)

# ============== INITIALIZE MT5 ================

def initialize_mt5():
    """Initialize MT5 with proper error handling"""
    
    print("=" * 60)
    print("🤖 INITIALIZING MT5 CONNECTION...")
    print("=" * 60)
    
    # Initialize MT5
    if not mt5.initialize():
        error = mt5.last_error()
        print(f"❌ MT5 INIT FAILED: {error}")
        print("\n🔧 SOLUTIONS:")
        print("1. Make sure MetaTrader 5 is installed")
        print("2. Start MetaTrader 5 and login to your account")
        print("3. Check if your broker supports MT5")
        print("4. Run Python as Administrator")
        raise Exception(f"MT5 initialization failed: {error}")
    
    print("✅ MT5 initialized successfully")
    
    # Get account info
    account = mt5.account_info()
    if account is None:
        print("❌ Failed to get account info")
        print("💡 Please login to MT5 manually first")
        mt5.shutdown()
        raise Exception("Account info not available")
    
    print(f"📊 Account: {account.login}")
    print(f"💰 Balance: ${account.balance:.2f}")
    print(f"📈 Equity: ${account.equity:.2f}")
    print(f"📉 Free Margin: ${account.margin_free:.2f}")
    
    # Check symbol
    print(f"🔍 Checking symbol: {SYMBOL}")
    symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        print(f"❌ Symbol '{SYMBOL}' not found")
        mt5.shutdown()
        raise Exception(f"Symbol {SYMBOL} not found")
    
    print(f"✅ Symbol found: {SYMBOL}")
    print(f"💵 Bid: {symbol_info.bid}")
    print(f"💰 Ask: {symbol_info.ask}")
    print(f"📊 Spread: {symbol_info.spread}")
    
    # Enable symbol if needed
    if not symbol_info.visible:
        mt5.symbol_select(SYMBOL, True)
        print(f"✅ Symbol '{SYMBOL}' enabled")
    
    print("=" * 60)
    print("🚀 MT5 READY FOR TRADING")
    print("=" * 60)
    
    return True

# ============= SHUTDOWN ================

def shutdown_mt5():
    mt5.shutdown()
    print("🛑 MT5 shutdown")

# ============== ACCOUNT INFO ==================

def get_account_info():
    return mt5.account_info()

# ============ SYMBOL INFO =================

def get_symbol_info():
    return mt5.symbol_info(SYMBOL)

# ============== GET TICK ================

def get_tick():
    return mt5.symbol_info_tick(SYMBOL)

# ============== GET POSITIONS ==============

def get_positions():
    return mt5.positions_get(symbol=SYMBOL)

# ============== PLACE ORDER ================

def place_order(direction, volume, sl, tp):
    """Place order with SL and TP"""
    
    tick = get_tick()
    if tick is None:
        print("❌ NO TICK DATA")
        return None
    
    # Determine order type
    if direction == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
    else:
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
    
    # Create order request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "magic": MAGIC,
        "deviation": 50,
        "comment": "BTC_AI_BOT"
    }
    
    print(f"📊 Opening {direction} at {price:.2f}")
    print(f"📉 SL: {sl:.2f} ({abs(price-sl):.2f} pts)")
    print(f"📈 TP: {tp:.2f} ({abs(tp-price):.2f} pts)")
    
    # Send order
    result = mt5.order_send(request)
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"✅ Trade opened! Ticket: {result.order}")
        return result
    else:
        print(f"❌ Order failed: {result.retcode} - {result.comment}")
        return None

# =========== MODIFY POSITION ===============

def modify_position(ticket, sl, tp):
    """Modify SL/TP for existing position"""
    
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": ticket,
        "sl": sl,
        "tp": tp
    }
    
    result = mt5.order_send(request)
    return result

# ============== CLOSE POSITION ================

def close_trade(position):
    """Close a position"""
    
    tick = get_tick()
    if tick is None:
        print("❌ NO TICK DATA")
        return None
    
    # Determine close direction
    if position.type == 0:  # BUY
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
    else:  # SELL
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": SYMBOL,
        "volume": position.volume,
        "type": order_type,
        "position": position.ticket,
        "price": price,
        "deviation": 50,
        "magic": MAGIC,
        "comment": "CLOSE_TRADE"
    }
    
    result = mt5.order_send(request)
    return result

# ============== GET CANDLES ================

def get_candles(limit=500):
    """Get candles from MT5"""
    
    rates = mt5.copy_rates_from_pos(
        SYMBOL,
        TIMEFRAME,
        0,
        limit
    )
    
    if rates is None or len(rates) == 0:
        print("❌ Failed to get candle data")
        return None
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.rename(columns={
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'tick_volume': 'volume'
    }, inplace=True)
    
    return df

# ============== TEST CONNECTION ================

def test_connection():
    """Test MT5 connection"""
    print("Testing MT5 Connection...")
    print("=" * 60)
    
    try:
        initialize_mt5()
        print("\n✅ MT5 Connection Test Passed!")
        shutdown_mt5()
        return True
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        return False

# If run directly, test the connection
if __name__ == "__main__":
    test_connection()