"""Historical-data utilities. Live candle access belongs to mt5_connector."""
import pandas as pd


def clean_data(df):
    required = {"time", "open", "high", "low", "close", "volume"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Historical data missing columns: {sorted(missing)}")
    result = df.copy()
    result["time"] = pd.to_datetime(result["time"], utc=True)
    for column in required - {"time"}:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    return result.dropna().drop_duplicates("time").sort_values("time").reset_index(drop=True)
