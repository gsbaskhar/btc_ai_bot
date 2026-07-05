# test_mt5.py
import MetaTrader5 as mt5
import sys

print("Testing MT5 Connection...")
print("=" * 60)

# Initialize MT5
if not mt5.initialize():
    print(f"❌ MT5 Init Failed: {mt5.last_error()}")
    sys.exit(1)

print("✅ MT5 Initialized")

# Get account info
account = mt5.account_info()
if account:
    print(f"✅ Account: {account.login}")
    print(f"💰 Balance: ${account.balance:.2f}")
    print(f"📊 Leverage: {account.leverage}x")
else:
    print("❌ No account info - Please login to MT5")
    mt5.shutdown()
    sys.exit(1)

# Check BTCUSD symbol
symbol = "BTCUSD"
symbol_info = mt5.symbol_info(symbol)
if symbol_info:
    print(f"✅ Symbol: {symbol}")
    print(f"💵 Bid: {symbol_info.bid}")
    print(f"💰 Ask: {symbol_info.ask}")
    print(f"📊 Spread: {symbol_info.spread}")
else:
    print(f"❌ Symbol {symbol} not found")

mt5.shutdown()
print("=" * 60)
print("Test Complete!")