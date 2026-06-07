import MetaTrader5 as mt5

from config import *

# ============== INITIALIZE MT5 ================

def initialize_mt5():

    if not mt5.initialize():

        raise Exception(
            f"MT5 INIT FAILED: {mt5.last_error()}"
        )

    info = mt5.symbol_info(SYMBOL)

    if info is None:

        raise Exception(
            f"SYMBOL NOT FOUND: {SYMBOL}"
        )

    if not info.visible:

        mt5.symbol_select(SYMBOL, True)

    account = mt5.account_info()

    print("=" * 60)

    print("MT5 CONNECTED")

    print(f"BALANCE : {account.balance}")

    print(f"EQUITY  : {account.equity}")

    print("=" * 60)

# ============= SHUTDOWN ================

def shutdown_mt5():

    mt5.shutdown()

# ============== ACCOUNT INFO ==================

def get_account_info():

    return mt5.account_info()

# ============ SYMBOL INFO =================

def get_symbol_info():

    return mt5.symbol_info(SYMBOL)

# ============== GET TICK ================

def get_tick():

    return mt5.symbol_info_tick(SYMBOL)

# ============== GET POSITIONS ==============

def get_positions():

    return mt5.positions_get(symbol=SYMBOL)

# ============== PLACE ORDER ================

def place_order(direction, volume, sl, tp):

    tick = get_tick()

    if tick is None:

        print("NO TICK DATA")

        return None

    # ============= BUY ==================

    if direction == "BUY":

        order_type = mt5.ORDER_TYPE_BUY

        price = tick.ask

    # =========== SELL ==================

    else:

        order_type = mt5.ORDER_TYPE_SELL

        price = tick.bid

    # ============ REQUEST =================

    request = {

        "action": mt5.TRADE_ACTION_DEAL,

        "symbol": SYMBOL,

        "volume": volume,

        "type": order_type,

        "price": price,

        "sl": sl,

        "tp": tp,

        "magic": MAGIC,

        "deviation": 100,

        "comment": "BTC_AI_BOT"
    }

    print("=" * 60)

    print(f"OPENING {direction}")

    print(f"ENTRY : {price}")

    print(f"SL    : {sl}")

    print(f"TP    : {tp}")

    print("=" * 60)

    # ============= SEND ORDER ===============

    result = mt5.order_send(request)

    return result

# =========== MODIFY POSITION ===============

def modify_position(ticket, sl, tp):

    request = {

        "action": mt5.TRADE_ACTION_SLTP,

        "position": ticket,

        "sl": sl,

        "tp": tp
    }

    result = mt5.order_send(request)

    return result

# ============== CLOSE POSITION ================

def close_trade(position):

    tick = get_tick()

    if position.type == 0:

        order_type = mt5.ORDER_TYPE_SELL

        price = tick.bid

    else:

        order_type = mt5.ORDER_TYPE_BUY

        price = tick.ask

    request = {

        "action": mt5.TRADE_ACTION_DEAL,

        "symbol": SYMBOL,

        "volume": position.volume,

        "type": order_type,

        "position": position.ticket,

        "price": price,

        "deviation": 100,

        "magic": MAGIC,

        "comment": "CLOSE_TRADE"
    }

    result = mt5.order_send(request)

    return result