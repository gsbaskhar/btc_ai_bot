import os
import MetaTrader5 as mt5

from config import *

# ============== INITIALIZE MT5 ================

def _find_mt5_terminal():

    candidates = []

    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")

    candidates.extend([
        os.path.join(program_files, "MetaTrader 5", "terminal64.exe"),
        os.path.join(program_files, "MetaTrader 5", "terminal.exe"),
        os.path.join(program_files_x86, "MetaTrader 5", "terminal64.exe"),
        os.path.join(program_files_x86, "MetaTrader 5", "terminal.exe"),
        os.path.join(program_files, "OctaFX", "MetaTrader 5", "terminal64.exe"),
        os.path.join(program_files, "OctaFX", "MetaTrader 5", "terminal.exe"),
    ])

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    return None


def initialize_mt5():

    terminal_path = MT5_PATH or _find_mt5_terminal()

    if terminal_path:
        initialized = mt5.initialize(path=terminal_path)
    else:
        initialized = mt5.initialize()

    if not initialized:
        error_code, error_message = mt5.last_error()
        raise Exception(
            f"MT5 INIT FAILED: ({error_code}) {error_message} - MT5_PATH={MT5_PATH} detected_path={terminal_path}"
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