"""Read-only connection and symbol check for the MT5 BTCUSD bot."""
import sys

import MetaTrader5 as mt5


print("Testing MT5 connection...")
print("=" * 60)
if not mt5.initialize():
    print(f"[ERROR] MT5 initialization failed: {mt5.last_error()}")
    sys.exit(1)

try:
    account = mt5.account_info()
    if account is None:
        print("[ERROR] No account information; log in to MT5 first.")
        sys.exit(1)
    print("[OK] MT5 initialized")
    print(f"[OK] Account: {account.login}")
    print(f"[OK] Balance: ${account.balance:.2f}")
    print(f"[OK] Leverage: {account.leverage}x")

    symbol = "BTCUSD"
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"[ERROR] Symbol {symbol} was not found in Market Watch.")
        sys.exit(1)
    print(f"[OK] Symbol: {symbol}")
    print(f"[OK] Bid: {symbol_info.bid}")
    print(f"[OK] Ask: {symbol_info.ask}")
    print(f"[OK] Spread: {symbol_info.spread}")
finally:
    mt5.shutdown()

print("=" * 60)
print("Test complete.")
