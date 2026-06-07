from config import *

from mt5_connector import modify_position, get_symbol_info

# ============ BREAK EVEN ===============

def apply_break_even(positions, tick):

    symbol_info = get_symbol_info()

    if symbol_info is None:
        return

    point = symbol_info.point

    for pos in positions:

        current = tick.bid if pos.type == 0 else tick.ask

        profit_points = abs(current - pos.price_open) / point

        # ========== BREAK EVEN =============

        if profit_points < BREAK_EVEN_TRIGGER:
            continue

        # compute a safe break-even price (add small buffer to avoid spread loss)
        buffer = point * 2

        if pos.type == 0:  # BUY -> move SL up
            be_price = pos.price_open + buffer
            # only update if it improves the current SL
            if pos.sl is None or pos.sl < be_price:
                modify_position(pos.ticket, be_price, pos.tp)
                print("BREAK EVEN ACTIVATED")

        else:  # SELL -> move SL down
            be_price = pos.price_open - buffer
            if pos.sl is None or pos.sl > be_price:
                modify_position(pos.ticket, be_price, pos.tp)
                print("BREAK EVEN ACTIVATED")

# =========== TRAILING STOP ==============

def apply_trailing_stop(positions, tick):

    symbol_info = get_symbol_info()

    if symbol_info is None:
        return

    point = symbol_info.point

    for pos in positions:

        current = tick.bid if pos.type == 0 else tick.ask

        profit_points = abs(current - pos.price_open) / point

        # ========== TRAILING TRIGGER ==============

        if profit_points < TRAILING_TRIGGER:
            continue

        # compute distance in price units
        dist = TRAILING_DISTANCE * point

        if pos.type == 0:  # BUY -> SL follows below current
            new_sl = current - dist
            # only update if new SL is greater than current SL (i.e. improves it)
            if pos.sl is None or new_sl > pos.sl:
                modify_position(pos.ticket, new_sl, pos.tp)
                print("TRAILING UPDATED")

        else:  # SELL -> SL follows above current
            new_sl = current + dist
            if pos.sl is None or new_sl < pos.sl:
                modify_position(pos.ticket, new_sl, pos.tp)
                print("TRAILING UPDATED")