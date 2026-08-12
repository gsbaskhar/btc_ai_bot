"""Append-only audit log for bot orders and closed MT5 deals."""
import csv
import os
from datetime import datetime, timezone

import MetaTrader5 as mt5
from config import MAGIC, SYMBOL

ORDER_LOG = "logs/orders.csv"
CLOSED_DEAL_LOG = "logs/closed_deals.csv"


def _ensure_file(path, headers):
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(headers)


def initialize_log():
    _ensure_file(ORDER_LOG, ["time_utc", "order_ticket", "direction", "volume", "price", "sl", "tp"])
    _ensure_file(CLOSED_DEAL_LOG, ["deal_ticket", "time_utc", "position_id", "deal_side", "volume", "price", "pnl"])


def log_order(result, direction, volume, sl, tp):
    with open(ORDER_LOG, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([datetime.now(timezone.utc).isoformat(), result.order, direction, volume, result.price, sl, tp])


def get_initial_stop(ticket):
    """Return the bot-recorded initial SL for a position, if available."""
    if not os.path.exists(ORDER_LOG):
        return None
    with open(ORDER_LOG, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["order_ticket"] == str(ticket):
                return float(row["sl"])
    return None


def daily_order_count(now=None):
    """Count today's successful bot entries from the local audit log.

    MT5 account history can lag immediately after an order, so it must not be
    the sole source for enforcing the daily entry cap.
    """
    if not os.path.exists(ORDER_LOG):
        return 0
    today = (now or datetime.now(timezone.utc)).date()
    with open(ORDER_LOG, newline="", encoding="utf-8") as f:
        return sum(
            datetime.fromisoformat(row["time_utc"]).date() == today
            for row in csv.DictReader(f)
        )


def sync_closed_deals():
    """Log each closed deal once, returning its net P/L for the session."""
    _ensure_file(CLOSED_DEAL_LOG, ["deal_ticket", "time_utc", "position_id", "deal_side", "volume", "price", "pnl"])
    with open(CLOSED_DEAL_LOG, newline="", encoding="utf-8") as f:
        seen = {row["deal_ticket"] for row in csv.DictReader(f)}
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    deals = mt5.history_deals_get(start, now) or ()
    added = []
    with open(CLOSED_DEAL_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for d in deals:
            if (str(d.ticket) in seen or d.symbol != SYMBOL or d.magic != MAGIC or
                    d.entry not in (mt5.DEAL_ENTRY_OUT, mt5.DEAL_ENTRY_OUT_BY)):
                continue
            pnl = d.profit + d.swap + d.commission
            direction = "BUY" if d.type == mt5.DEAL_TYPE_BUY else "SELL"
            writer.writerow([d.ticket, datetime.fromtimestamp(d.time, timezone.utc).isoformat(), d.position_id, direction, d.volume, d.price, pnl])
            added.append(pnl)
    return added
