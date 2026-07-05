# strategy/enhanced_strategy.py
import pandas as pd
import numpy as np
from config import *

def get_trend(df):
    """Enhanced trend detection with multiple confirmations"""
    
    last = df.iloc[-1]
    
    # EMA Trend
    bullish_ema = last["close"] > last["ema200"] and last["ema50"] > last["ema200"]
    bearish_ema = last["close"] < last["ema200"] and last["ema50"] < last["ema200"]
    
    # Price vs Bollinger
    bullish_bb = last["close"] > last["bb_middle"]
    bearish_bb = last["close"] < last["bb_middle"]
    
    # MACD
    bullish_macd = last["macd"] > last["macd_signal"]
    bearish_macd = last["macd"] < last["macd_signal"]
    
    # RSI
    bullish_rsi = last["rsi"] > 45
    bearish_rsi = last["rsi"] < 55
    
    # Volume confirmation
    volume_ok = last["volume_ratio"] > MIN_VOLUME_RATIO
    
    # Count confirmations
    bullish_score = sum([bullish_ema, bullish_bb, bullish_macd, bullish_rsi, volume_ok])
    bearish_score = sum([bearish_ema, bearish_bb, bearish_macd, bearish_rsi, volume_ok])
    
    # Require at least 3 confirmations
    if bullish_score >= 3:
        return "BULLISH"
    elif bearish_score >= 3:
        return "BEARISH"
    else:
        return "SIDEWAYS"


def get_breakout_signal(df, trend, debug=False):
    """Enhanced breakout strategy with multiple filters"""
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Strong candle detection
    body = abs(last["close"] - last["open"])
    avg_body = abs(df["close"] - df["open"]).tail(20).mean()
    strong_candle = body >= avg_body * 0.6  # Reduced from 0.7
    
    # Breakout detection
    bullish_breakout = last["close"] > prev["high"]
    bearish_breakout = last["close"] < prev["low"]
    
    # Volume confirmation
    volume_ok = last["volume_ratio"] >= MIN_VOLUME_RATIO
    
    # RSI filter (avoid extremes)
    rsi_ok_buy = last["rsi"] < RSI_OVERBOUGHT and last["rsi"] > RSI_OVERSOLD
    rsi_ok_sell = last["rsi"] < RSI_OVERBOUGHT and last["rsi"] > RSI_OVERSOLD
    
    # ATR filter
    atr_ok = MIN_ATR <= last["atr"] <= MAX_ATR
    
    # Order block confirmation
    ob_buy = last["bullish_ob"]
    ob_sell = last["bearish_ob"]
    
    # Liquidity sweep detection
    buy_liquidity = last["buy_liquidity"]
    sell_liquidity = last["sell_liquidity"]
    
    # BUY Signal (Relaxed)
    buy = (
        trend == "BULLISH" and
        bullish_breakout and
        strong_candle and
        volume_ok and
        rsi_ok_buy and
        atr_ok and
        (ob_buy or buy_liquidity or True)  # Always allow if other conditions met
    )
    
    # SELL Signal (Relaxed)
    sell = (
        trend == "BEARISH" and
        bearish_breakout and
        strong_candle and
        volume_ok and
        rsi_ok_sell and
        atr_ok and
        (ob_sell or sell_liquidity or True)  # Always allow if other conditions met
    )
    
    # Also check for pure liquidity sweep signals
    if not buy and not sell:
        if buy_liquidity and trend == "BULLISH":
            print("💧 BUY LIQUIDITY SWEEP - BUY")
            return "BUY"
        if sell_liquidity and trend == "BEARISH":
            print("💧 SELL LIQUIDITY SWEEP - SELL")
            return "SELL"
    
    if debug:
        print("=" * 60)
        print(f"📊 SIGNAL ANALYSIS")
        print("=" * 60)
        print(f"Trend          : {trend}")
        print(f"Close          : {last['close']:.2f}")
        print(f"EMA50          : {last['ema50']:.2f}")
        print(f"EMA200         : {last['ema200']:.2f}")
        print(f"RSI            : {last['rsi']:.2f}")
        print(f"ATR            : {last['atr']:.2f}")
        print(f"Volume Ratio   : {last['volume_ratio']:.2f}")
        print(f"Strong Candle  : {strong_candle}")
        print(f"Breakout       : {'BUY' if bullish_breakout else 'SELL' if bearish_breakout else 'NONE'}")
        print(f"Order Block    : {'BUY' if ob_buy else 'SELL' if ob_sell else 'NONE'}")
        print(f"Liquidity      : {'BUY' if buy_liquidity else 'SELL' if sell_liquidity else 'NONE'}")
        print("=" * 60)
    
    if buy:
        print("🟢 BUY SIGNAL DETECTED")
        return "BUY"
    elif sell:
        print("🔴 SELL SIGNAL DETECTED")
        return "SELL"
    
    return None


def get_liquidity_signal(df):
    """Liquidity sweep strategy"""
    
    last = df.iloc[-1]
    
    if last["buy_liquidity"]:
        print("💧 BUY SIDE LIQUIDITY TAKEN")
        return "BUY"
    
    if last["sell_liquidity"]:
        print("💧 SELL SIDE LIQUIDITY TAKEN")
        return "SELL"
    
    return None