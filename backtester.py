"""Closed-candle, multi-bar historical backtest for the active MT5 strategy."""
import sys
import pandas as pd

from data_handler import clean_data
from indicators import add_all_indicators
from risk_manager import calculate_sl_tp
from strategy.enhanced_strategy import (
    get_breakout_signal, 
    get_trend, 
    reset_loss_memory,
    _record_loss,
    _record_win
)


def load_candles_from_csv(csv_file):
    return clean_data(pd.read_csv(csv_file))


def run_backtest(df, max_trades=None):
    df = add_all_indicators(clean_data(df))
    reset_loss_memory()  # FIXED: Reset loss memory at start
    
    trades, next_allowed = [], 250
    bar_index = 250
    
    for i in range(250, len(df) - 1):
        if i < next_allowed:
            continue
        window = df.iloc[:i + 1]
        
        # FIXED: Pass bar_index for loss memory
        signal = get_breakout_signal(window, get_trend(window), debug=False, bar_index=i)
        
        if not signal:
            continue
        
        entry_bar = df.iloc[i + 1]
        entry, atr = entry_bar.open, window.atr.iloc[-1]
        
        # FIXED: Use wider stop with enforce_broker_minimum=False for backtest
        sl, tp = calculate_sl_tp(signal, entry, atr, enforce_broker_minimum=False)
        
        exit_price, exit_time, exit_type = entry_bar.close, entry_bar.time, "END"
        
        for j in range(i + 1, len(df)):
            bar = df.iloc[j]
            # Conservative convention: when SL and TP touch in one candle, SL wins.
            if signal == "BUY" and bar.low <= sl:
                exit_price, exit_time, exit_type = sl, bar.time, "SL"
                break
            if signal == "SELL" and bar.high >= sl:
                exit_price, exit_time, exit_type = sl, bar.time, "SL"
                break
            if signal == "BUY" and bar.high >= tp:
                exit_price, exit_time, exit_type = tp, bar.time, "TP"
                break
            if signal == "SELL" and bar.low <= tp:
                exit_price, exit_time, exit_type = tp, bar.time, "TP"
                break
        
        pnl_points = (exit_price - entry) if signal == "BUY" else (entry - exit_price)
        
        # FIXED: Record win/loss for loss memory
        if pnl_points > 0:
            _record_win(entry)
        else:
            _record_loss(entry, i)
        
        trades.append({
            "time": entry_bar.time, 
            "exit_time": exit_time, 
            "signal": signal, 
            "entry": entry, 
            "sl": sl, 
            "tp": tp, 
            "exit": exit_price, 
            "exit_type": exit_type, 
            "profit_points": pnl_points
        })
        
        next_allowed = j + 2
        if max_trades and len(trades) >= max_trades:
            break
        
        bar_index = i
    
    return pd.DataFrame(trades)


def analyze_results(results):
    if results.empty:
        print("No trades.")
        return
    
    wins = (results.profit_points > 0).sum()
    losses = (results.profit_points < 0).sum()
    gross_loss = -results.loc[results.profit_points < 0, "profit_points"].sum()
    gross_profit = results.loc[results.profit_points > 0, "profit_points"].sum()
    
    print("=" * 60)
    print("BACKTEST RESULTS")
    print("=" * 60)
    print(f"Total Trades: {len(results)}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"Win Rate: {wins / len(results) * 100:.1f}%")
    print(f"Net Profit (points): {results.profit_points.sum():.2f}")
    print(f"Profit Factor: {gross_profit / gross_loss if gross_loss else float('inf'):.2f}")
    print(f"Average Win: {gross_profit / wins if wins else 0:.2f}")
    print(f"Average Loss: {-gross_loss / losses if losses else 0:.2f}")
    print("=" * 60)
    
    # FIXED: Show consecutive losses
    max_consecutive = 0
    current = 0
    for pnl in results.profit_points:
        if pnl < 0:
            current += 1
            max_consecutive = max(max_consecutive, current)
        else:
            current = 0
    print(f"Max Consecutive Losses: {max_consecutive}")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python backtester.py historical.csv")
    
    results = run_backtest(load_candles_from_csv(sys.argv[1]))
    results.to_csv("backtest_results.csv", index=False)
    analyze_results(results)