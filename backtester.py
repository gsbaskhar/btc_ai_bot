import pandas as pd

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