"""Closed-candle trend-following BTCUSD entry rules with loss memory."""
from config import MAX_ATR, MIN_ATR, MIN_VOLUME_RATIO, RSI_OVERBOUGHT, RSI_OVERSOLD

# FIXED: Track repeated losses at price levels
_recent_losses = {}
_MAX_LOSSES_AT_LEVEL = 2
_LEVEL_COOLDOWN_BARS = 5


def get_trend(df):
    last = df.iloc[-1]
    bullish = sum((
        last.close > last.ema200 and last.ema50 > last.ema200,
        last.close > last.bb_middle,
        last.macd > last.macd_signal,
        last.rsi >= 52,
        last.volume_ratio >= MIN_VOLUME_RATIO,
    ))
    bearish = sum((
        last.close < last.ema200 and last.ema50 < last.ema200,
        last.close < last.bb_middle,
        last.macd < last.macd_signal,
        last.rsi <= 48,
        last.volume_ratio >= MIN_VOLUME_RATIO,
    ))
    if bullish >= 4:
        return "BULLISH"
    if bearish >= 4:
        return "BEARISH"
    return "SIDEWAYS"


def _is_price_blacklisted(entry_price, bar_index):
    """Check if we've lost too many times at this price level."""
    # Round to nearest 50 points to group similar levels
    level = round(entry_price / 50) * 50
    
    if level not in _recent_losses:
        return False
    
    losses = _recent_losses[level]
    if losses['count'] >= _MAX_LOSSES_AT_LEVEL:
        # Check if cooldown has expired
        if bar_index - losses['last_bar'] < _LEVEL_COOLDOWN_BARS:
            return True
        else:
            # Cooldown expired, reset
            _recent_losses[level]['count'] = 0
            return False
    return False


def _record_loss(entry_price, bar_index):
    """Record a loss at this price level."""
    level = round(entry_price / 50) * 50
    if level not in _recent_losses:
        _recent_losses[level] = {'count': 0, 'last_bar': bar_index}
    _recent_losses[level]['count'] += 1
    _recent_losses[level]['last_bar'] = bar_index


def _record_win(entry_price):
    """Reset loss count on a win."""
    level = round(entry_price / 50) * 50
    if level in _recent_losses:
        _recent_losses[level]['count'] = 0


def reset_loss_memory():
    """Reset all loss memory - call this when strategy restarts."""
    global _recent_losses
    _recent_losses = {}


def get_breakout_signal(df, trend, debug=False, bar_index=0):
    """Return a confirmed breakout with loss memory and trend confirmation."""
    last, prev = df.iloc[-1], df.iloc[-2]
    
    # FIXED: Ensure strong candle threshold is reasonable
    average_body = (df.close - df.open).abs().tail(20).mean()
    strong_candle = abs(last.close - last.open) >= average_body * 0.8
    volume_ok = last.volume_ratio >= MIN_VOLUME_RATIO
    atr_ok = MIN_ATR <= last.atr <= MAX_ATR
    rsi_ok = RSI_OVERSOLD < last.rsi < RSI_OVERBOUGHT
    
    # FIXED: Additional trend confirmation
    # Only sell if price is below EMA50 (bearish confirmation)
    # Only buy if price is above EMA50 (bullish confirmation)
    trend_confirmed = False
    
    buy = (
        trend == "BULLISH" and 
        last.close > prev.high and 
        last.close > last.ema50 and  # FIXED: Added trend confirmation
        strong_candle and 
        volume_ok and 
        atr_ok and 
        rsi_ok
    )
    
    sell = (
        trend == "BEARISH" and 
        last.close < prev.low and 
        last.close < last.ema50 and  # FIXED: Added trend confirmation
        strong_candle and 
        volume_ok and 
        atr_ok and 
        rsi_ok
    )
    
    # FIXED: Check if we're entering at a blacklisted price level
    if buy or sell:
        entry_price = last.close
        if _is_price_blacklisted(entry_price, bar_index):
            if debug:
                print(f"BLACKLISTED: Price level {entry_price} has too many recent losses")
            return None
    
    if debug:
        print(f"Signal: trend={trend}, RSI={last.rsi:.1f}, ATR={last.atr:.1f}, "
              f"volume={last.volume_ratio:.2f}, strong={strong_candle}")
        if buy:
            print("BUY SIGNAL (trend confirmed)")
        elif sell:
            print("SELL SIGNAL (trend confirmed)")
    
    return "BUY" if buy else "SELL" if sell else None


def get_liquidity_signal(df):
    # Kept for import compatibility. Raw liquidity sweeps are not entries.
    return None