"""Closed-candle trend-following BTCUSD entry rules."""
from config import MAX_ATR, MIN_ATR, MIN_VOLUME_RATIO, RSI_OVERBOUGHT, RSI_OVERSOLD


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


def get_breakout_signal(df, trend, debug=False):
    """Return a confirmed breakout only; never trade an unfiltered sweep."""
    last, prev = df.iloc[-1], df.iloc[-2]
    average_body = (df.close - df.open).abs().tail(20).mean()
    strong_candle = abs(last.close - last.open) >= average_body * 0.8
    volume_ok = last.volume_ratio >= MIN_VOLUME_RATIO
    atr_ok = MIN_ATR <= last.atr <= MAX_ATR
    rsi_ok = RSI_OVERSOLD < last.rsi < RSI_OVERBOUGHT
    buy = trend == "BULLISH" and last.close > prev.high and strong_candle and volume_ok and atr_ok and rsi_ok
    sell = trend == "BEARISH" and last.close < prev.low and strong_candle and volume_ok and atr_ok and rsi_ok
    if debug:
        print(f"Signal: trend={trend}, RSI={last.rsi:.1f}, ATR={last.atr:.1f}, volume={last.volume_ratio:.2f}, strong={strong_candle}")
    return "BUY" if buy else "SELL" if sell else None


def get_liquidity_signal(df):
    # Kept for import compatibility. Raw liquidity sweeps are not entries.
    return None