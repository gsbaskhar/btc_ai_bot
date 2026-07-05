import pandas as pd

from data_handler import clean_data
from indicators import add_all_indicators
from risk_manager import calculate_sl_tp
from strategy.trend_strategy import get_trend
from strategy.breakout_strategy import get_breakout_signal

# ============= BACKTEST RESULTS ============

def analyze_results(csv_file):

    df = pd.read_csv(csv_file)

    total_trades = len(df)

    wins = len(

        df[df['profit'] > 0]
    )

    losses = len(

        df[df['profit'] <= 0]
    )

    # ============= WINRATE ==============

    if total_trades > 0:

        winrate = (

            wins
            /
            total_trades
        ) * 100

    else:

        winrate = 0

    # ============ NET PROFIT ============

    total_profit = (

        df['profit']
        .sum()
    )

    # ============= PROFIT FACTOR =============

    gross_profit = (

        df[df['profit'] > 0]

        ['profit']

        .sum()
    )

    gross_loss = abs(

        df[df['profit'] <= 0]

        ['profit']

        .sum()
    )

    if gross_loss == 0:

        profit_factor = 0

    else:

        profit_factor = (

            gross_profit
            /
            gross_loss
        )

    # ============ OUTPUT ==============

    print("=" * 60)

    print(f"TOTAL TRADES : {total_trades}")

    print(f"WINS         : {wins}")

    print(f"LOSSES       : {losses}")

    print(f"WINRATE      : {winrate:.2f}%")

    print(f"NET PROFIT   : {total_profit:.2f}")

    print(f"PROFIT FACTOR: {profit_factor:.2f}")

    print("=" * 60)


def load_candles_from_csv(csv_file):
    df = pd.read_csv(csv_file, parse_dates=['time'])
    return clean_data(df)


def simulate_trade(signal, entry, sl, tp, bar):
    if signal == 'BUY':
        if bar['low'] <= sl:
            return sl - entry, sl, 'SL'
        if bar['high'] >= tp:
            return tp - entry, tp, 'TP'
        return bar['close'] - entry, bar['close'], 'CLOSE'

    if signal == 'SELL':
        if bar['high'] >= sl:
            return entry - sl, sl, 'SL'
        if bar['low'] <= tp:
            return entry - tp, tp, 'TP'
        return entry - bar['close'], bar['close'], 'CLOSE'

    return 0, entry, 'NONE'


def run_backtest(df, max_trades=None):
    df = clean_data(df)
    df = add_all_indicators(df)

    trades = []
    last_trade_index = -999

    for i in range(50, len(df) - 1):
        if i - last_trade_index <= 1:
            continue

        window = df.iloc[: i + 1]
        trend = get_trend(window)
        signal = get_breakout_signal(window, trend, debug=False)

        if signal is None:
            continue

        entry = df.iloc[i + 1]['open']
        atr = window['atr'].iloc[-1]
        sl, tp = calculate_sl_tp(signal, entry, atr)
        next_bar = df.iloc[i + 1]

        profit, exit_price, exit_type = simulate_trade(
            signal,
            entry,
            sl,
            tp,
            next_bar,
        )

        trades.append({
            'time': next_bar['time'],
            'signal': signal,
            'entry': entry,
            'sl': sl,
            'tp': tp,
            'exit': exit_price,
            'exit_type': exit_type,
            'profit': profit,
        })

        last_trade_index = i

        if max_trades and len(trades) >= max_trades:
            break

    return pd.DataFrame(trades)


def save_backtest_results(results, csv_file):
    results.to_csv(csv_file, index=False)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: python backtester.py path/to/historical.csv')
        sys.exit(1)

    hist_file = sys.argv[1]
    df = load_candles_from_csv(hist_file)
    results = run_backtest(df)
    save_backtest_results(results, 'backtest_results.csv')
    analyze_results('backtest_results.csv')
