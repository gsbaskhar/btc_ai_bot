import os
import pandas as pd
import matplotlib.pyplot as plt

# ============== EQUITY CURVE ================

def generate_equity_curve(csv_file):

    df = pd.read_csv(csv_file)

    df['equity'] = (

        df['profit']
        .cumsum()
    )

    plt.figure(

        figsize=(12, 6)
    )

    plt.plot(

        df['equity']
    )

    plt.title(

        "Equity Curve"
    )

    plt.xlabel("Trades")

    plt.ylabel("Profit")

    plt.grid(True)

    plt.show()


# ============== DAY-WISE REPORT ================

def generate_daywise_report(csv_file, out_file=None):

    df = pd.read_csv(csv_file)

    # ensure time column is datetime
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'])
        df['date'] = df['time'].dt.date
    else:
        raise ValueError('CSV must contain a "time" column')

    # basic aggregations per day
    grouped = df.groupby('date').agg(
        trades=('profit', 'count'),
        net_profit=('profit', 'sum'),
        wins=('profit', lambda x: (x > 0).sum()),
        losses=('profit', lambda x: (x <= 0).sum()),
        avg_profit=('profit', 'mean'),
        max_profit=('profit', 'max'),
        max_loss=('profit', 'min')
    )

    grouped['winrate'] = (grouped['wins'] / grouped['trades']).fillna(0) * 100

    # default output path
    if out_file is None:
        out_file = os.path.join('reports', 'daywise_report.csv')

    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    grouped.to_csv(out_file)

    print(f"Saved daywise report to {out_file}")

    return grouped