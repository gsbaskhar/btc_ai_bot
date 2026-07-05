import numpy as np

from ta.trend import EMAIndicator
from ta.trend import MACD

from ta.momentum import RSIIndicator

from ta.volatility import (
    AverageTrueRange,
    BollingerBands
)

from config import *


# ===================================
# EMA
# ===================================

def add_ema(df):

    df["ema50"] = EMAIndicator(

        df["close"],

        EMA_FAST

    ).ema_indicator()

    df["ema200"] = EMAIndicator(

        df["close"],

        EMA_SLOW

    ).ema_indicator()

    return df


# ===================================
# RSI
# ===================================

def add_rsi(df):

    df["rsi"] = RSIIndicator(

        df["close"],

        RSI_PERIOD

    ).rsi()

    return df


# ===================================
# ATR
# ===================================

def add_atr(df):

    atr = AverageTrueRange(

        high=df["high"],

        low=df["low"],

        close=df["close"],

        window=ATR_PERIOD

    )

    df["atr"] = atr.average_true_range()

    return df


# ===================================
# MACD
# ===================================

def add_macd(df):

    macd = MACD(

        close=df["close"],

        window_fast=MACD_FAST,

        window_slow=MACD_SLOW,

        window_sign=MACD_SIGNAL

    )

    df["macd"] = macd.macd()

    df["macd_signal"] = macd.macd_signal()

    df["macd_hist"] = macd.macd_diff()

    return df


# ===================================
# Bollinger
# ===================================

def add_bollinger(df):

    bb = BollingerBands(

        close=df["close"],

        window=BOLLINGER_PERIOD

    )

    df["bb_upper"] = bb.bollinger_hband()

    df["bb_middle"] = bb.bollinger_mavg()

    df["bb_lower"] = bb.bollinger_lband()

    return df


# ===================================
# Volume Ratio
# ===================================

def add_volume(df):

    df["volume_ma"] = (

        df["volume"]

        .rolling(20)

        .mean()

    )

    df["volume_ratio"] = (

        df["volume"]

        / df["volume_ma"]

    )

    return df


# ===================================
# Order Block
# ===================================

def add_orderblocks(df):

    df["bullish_ob"] = False

    df["bearish_ob"] = False

    for i in range(2, len(df)):

        if (

            df["close"].iloc[i]

            >

            df["high"].iloc[i-1]

        ):

            df.loc[

                df.index[i],

                "bullish_ob"

            ] = True

        if (

            df["close"].iloc[i]

            <

            df["low"].iloc[i-1]

        ):

            df.loc[

                df.index[i],

                "bearish_ob"

            ] = True

    return df


# ===================================
# Liquidity Sweep
# ===================================

def add_liquidity(df):

    df["buy_liquidity"] = False

    df["sell_liquidity"] = False

    for i in range(3, len(df)):

        prev_high = max(

            df["high"].iloc[i-3:i]

        )

        prev_low = min(

            df["low"].iloc[i-3:i]

        )

        if (

            df["high"].iloc[i]

            >

            prev_high

            and

            df["close"].iloc[i]

            <

            prev_high

        ):

            df.loc[

                df.index[i],

                "sell_liquidity"

            ] = True

        if (

            df["low"].iloc[i]

            <

            prev_low

            and

            df["close"].iloc[i]

            >

            prev_low

        ):

            df.loc[

                df.index[i],

                "buy_liquidity"

            ] = True

    return df


# ===================================
# ALL
# ===================================

def add_all_indicators(df):

    df = add_ema(df)

    df = add_rsi(df)

    df = add_atr(df)

    df = add_macd(df)

    df = add_bollinger(df)

    df = add_volume(df)

    df = add_orderblocks(df)

    df = add_liquidity(df)

    return df