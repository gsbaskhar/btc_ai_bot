# add_ema()

# add_rsi()

# add_atr()

# add_volume()

# add_all_indicators()

from ta.trend import EMAIndicator
from ta.trend import MACD

from ta.momentum import RSIIndicator

from ta.volatility import AverageTrueRange
from ta.volatility import BollingerBands

from config import *

# ============= EMA =================

def add_ema(df):

    close = df['close']

    df['ema50'] = EMAIndicator(

        close,

        EMA_FAST

    ).ema_indicator()

    df['ema200'] = EMAIndicator(

        close,

        EMA_SLOW

    ).ema_indicator()

    return df

# =============== RSI ===============

def add_rsi(df):

    close = df['close']

    df['rsi'] = RSIIndicator(

        close,

        RSI_PERIOD

    ).rsi()

    return df

# =============== ATR ===================

def add_atr(df):

    atr = AverageTrueRange(

        high=df['high'],

        low=df['low'],

        close=df['close'],

        window=ATR_PERIOD
    )

    df['atr'] = atr.average_true_range()

    return df

# ============ VOLUME ===============

def add_volume(df):

    df['volume_ma'] = (

        df['tick_volume']

        .rolling(20)

        .mean()
    )

    df['volume_ratio'] = (

        df['tick_volume']

        / df['volume_ma']
    )

    return df

# =========== MACD ===============

def add_macd(df):

    macd = MACD(

        close=df['close'],

        window_slow=26,

        window_fast=12,

        window_sign=9
    )

    df['macd'] = macd.macd()

    df['macd_signal'] = macd.macd_signal()

    df['macd_histogram'] = macd.macd_diff()

    return df

# ============ BOLLINGER BANDS =============

def add_bollinger(df):

    bb = BollingerBands(

        close=df['close'],

        window=20,

        window_dev=2
    )

    df['bb_upper'] = bb.bollinger_hband()

    df['bb_middle'] = bb.bollinger_mavg()

    df['bb_lower'] = bb.bollinger_lband()

    return df

# ================ ORDER BLOCKS ==================

def add_orderblocks(df):

    df['bullish_ob'] = False

    df['bearish_ob'] = False

    for i in range(2, len(df)):

        prev = df.iloc[i - 1]

        current = df.iloc[i]

        # ========= Bullish Order Block ===========

        if (

            prev.close < prev.open

            and

            current.close > prev.high

        ):

            df.at[df.index[i - 1], 'bullish_ob'] = True

        # ========= Bearish Order Block ===========

        if (

            prev.close > prev.open

            and

            current.close < prev.low

        ):

            df.at[df.index[i - 1], 'bearish_ob'] = True

    return df

# ============ LIQUIDITY SWEEPS ============

def add_liquidity(df):

    df['buy_liquidity_sweep'] = False

    df['sell_liquidity_sweep'] = False

    for i in range(2, len(df)):

        prev = df.iloc[i - 1]

        current = df.iloc[i]

        body = abs(

            current.close - current.open
        )

        upper_wick = (

            current.high
            -
            max(current.open, current.close)
        )

        lower_wick = (

            min(current.open, current.close)
            -
            current.low
        )

        # ======== Sell-side liquidity sweep =========

        if lower_wick > body * 2:

            df.at[
                df.index[i],
                'buy_liquidity_sweep'
            ] = True

        # ========= Buy-side liquidity sweep =========

        if upper_wick > body * 2:

            df.at[
                df.index[i],
                'sell_liquidity_sweep'
            ] = True

    return df

# =========== ALL INDICATORS ===============

def add_all_indicators(df):

    df = add_ema(df)

    df = add_rsi(df)

    df = add_atr(df)

    df = add_volume(df)

    df = add_macd(df)

    df = add_bollinger(df)

    df = add_orderblocks(df)

    df = add_liquidity(df)

    return df