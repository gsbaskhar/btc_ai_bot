# risk_manager.py
from config import *
import MetaTrader5 as mt5
from datetime import datetime

# Make sure MIN_LOT_SIZE and MAX_LOT_SIZE exist
try:
    MIN_LOT_SIZE
except NameError:
    MIN_LOT_SIZE = 0.01

try:
    MAX_LOT_SIZE
except NameError:
    MAX_LOT_SIZE = 0.10

def calculate_position_size(price, atr):
    """Calculate position size based on risk"""
    
    account = mt5.account_info()
    if account is None:
        return LOT_SIZE
    
    # Risk amount (1% of account)
    risk_amount = account.balance * (RISK_PERCENT / 100)
    
    # SL distance in points
    sl_distance = atr * ATR_MULTIPLIER
    
    if sl_distance == 0:
        sl_distance = 100  # Fallback
    
    # Position size
    lot_size = risk_amount / sl_distance
    
    # Adjust for BTC
    lot_size = lot_size * 0.01
    
    # Round to valid lot size
    lot_size = max(MIN_LOT_SIZE, min(MAX_LOT_SIZE, round(lot_size, 2)))
    
    # Safety checks
    if lot_size < MIN_LOT_SIZE:
        lot_size = MIN_LOT_SIZE
    if lot_size > MAX_LOT_SIZE:
        lot_size = MAX_LOT_SIZE
    
    print(f"📊 Position Size: {lot_size:.2f}")
    print(f"💰 Risk Amount: ${risk_amount:.2f}")
    print(f"📉 SL Distance: {sl_distance:.2f} pts")
    
    return lot_size


def calculate_sl_tp(signal, entry, atr):
    """Calculate SL and TP levels"""
    
    sl_distance = atr * ATR_MULTIPLIER
    
    if sl_distance < 10:
        sl_distance = 100  # Minimum stop distance
    
    if signal == "BUY":
        sl = entry - sl_distance
        tp = entry + (sl_distance * RISK_REWARD)
    else:
        sl = entry + sl_distance
        tp = entry - (sl_distance * RISK_REWARD)
    
    return sl, tp


def check_daily_loss():
    """Check if daily loss limit is reached"""
    
    today = datetime.now()
    start_of_day = datetime(today.year, today.month, today.day)
    
    deals = mt5.history_deals_get(start_of_day, today)
    if deals is None or len(deals) == 0:
        return False
    
    # Calculate P/L
    total_loss = 0
    for deal in deals:
        if deal.profit < 0:
            total_loss += abs(deal.profit)
    
    account = mt5.account_info()
    if account is None:
        return False
    
    loss_percent = (total_loss / account.balance) * 100
    
    if loss_percent >= MAX_DAILY_LOSS:
        print(f"⚠️ DAILY LOSS LIMIT REACHED: {loss_percent:.2f}%")
        return True
    
    return False


def check_consecutive_losses():
    """Check consecutive losses"""
    
    today = datetime.now()
    start_of_day = datetime(today.year, today.month, today.day)
    
    deals = mt5.history_deals_get(start_of_day, today)
    if deals is None or len(deals) == 0:
        return False
    
    # Check last trades
    losses = 0
    for deal in reversed(deals):
        if deal.profit < 0:
            losses += 1
            if losses >= MAX_CONSECUTIVE_LOSSES:
                print(f"⚠️ MAX CONSECUTIVE LOSSES REACHED: {losses}")
                return True
        else:
            break
    
    return False