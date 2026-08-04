import os
import pandas as pd
import matplotlib.pyplot as plt


def _load_results(csv_file):
    df = pd.read_csv(csv_file)
    # Supports the new MT5 closed-deal log and point-based backtest output.
    if "pnl" in df:
        df = df.rename(columns={"pnl": "profit"})
    elif "profit_points" in df:
        df = df.rename(columns={"profit_points": "profit"})
    if "profit" not in df or "time" not in df:
        raise ValueError("CSV must contain time plus pnl, profit, or profit_points")
    df["time"] = pd.to_datetime(df["time"], utc=True)
    return df


def generate_equity_curve(csv_file):
    df = _load_results(csv_file)
    df["equity"] = df.profit.cumsum()
    plt.figure(figsize=(12, 6))
    plt.plot(df.equity)
    plt.title("Equity Curve")
    plt.xlabel("Trades")
    plt.ylabel("P/L (account currency or backtest points)")
    plt.grid(True)
    plt.show()


def generate_daywise_report(csv_file, out_file="reports/daywise_report.csv"):
    df = _load_results(csv_file)
    df["date"] = df.time.dt.date
    grouped = df.groupby("date").agg(
        trades=("profit", "count"), net_profit=("profit", "sum"),
        wins=("profit", lambda x: (x > 0).sum()), losses=("profit", lambda x: (x <= 0).sum()),
        avg_profit=("profit", "mean"), max_profit=("profit", "max"), max_loss=("profit", "min"),
    )
    grouped["winrate"] = grouped.wins / grouped.trades * 100
    directory = os.path.dirname(out_file)
    if directory:
        os.makedirs(directory, exist_ok=True)
    grouped.to_csv(out_file)
    return grouped
