"""Closed-candle, multi-bar historical backtest for the active MT5 strategy."""
import sys
import pandas as pd

from data_handler import clean_data
from indicators import add_all_indicators
from risk_manager import calculate_sl_tp
from strategy.enhanced_strategy import get_breakout_signal, get_trend


def load_candles_from_csv(csv_file):
    return clean_data(pd.read_csv(csv_file))


def run_backtest(df, max_trades=None):
    df = add_all_indicators(clean_data(df))
    trades, next_allowed = [], 250
    for i in range(250, len(df) - 1):
        if i < next_allowed:
            continue
        window = df.iloc[:i + 1]
        signal = get_breakout_signal(window, get_trend(window))
        if not signal:
            continue
        entry_bar = df.iloc[i + 1]
        entry, atr = entry_bar.open, window.atr.iloc[-1]
        sl, tp = calculate_sl_tp(signal, entry, atr, enforce_broker_minimum=False)
        exit_price, exit_time, exit_type = entry_bar.close, entry_bar.time, "END"
        for j in range(i + 1, len(df)):
            bar = df.iloc[j]
            # Conservative convention: when SL and TP touch in one candle, SL wins.
            if signal == "BUY" and bar.low <= sl:
                exit_price, exit_time, exit_type = sl, bar.time, "SL"; break
            if signal == "SELL" and bar.high >= sl:
                exit_price, exit_time, exit_type = sl, bar.time, "SL"; break
            if signal == "BUY" and bar.high >= tp:
                exit_price, exit_time, exit_type = tp, bar.time, "TP"; break
            if signal == "SELL" and bar.low <= tp:
                exit_price, exit_time, exit_type = tp, bar.time, "TP"; break
        pnl_points = (exit_price - entry) if signal == "BUY" else (entry - exit_price)
        trades.append({"time": entry_bar.time, "exit_time": exit_time, "signal": signal, "entry": entry, "sl": sl, "tp": tp, "exit": exit_price, "exit_type": exit_type, "profit_points": pnl_points})
        next_allowed = j + 2
        if max_trades and len(trades) >= max_trades:
            break
    return pd.DataFrame(trades)


def analyze_results(results):
    if results.empty:
        print("No trades."); return
    wins = (results.profit_points > 0).sum()
    gross_loss = -results.loc[results.profit_points < 0, "profit_points"].sum()
    gross_profit = results.loc[results.profit_points > 0, "profit_points"].sum()
    print(f"Trades: {len(results)} | Win rate: {wins / len(results) * 100:.1f}% | Net points: {results.profit_points.sum():.2f} | PF: {gross_profit / gross_loss if gross_loss else float('inf'):.2f}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python backtester.py historical.csv")
    results = run_backtest(load_candles_from_csv(sys.argv[1]))
    results.to_csv("backtest_results.csv", index=False)
    analyze_results(results)
