from datetime import datetime

# =========== LONDON + NY SESSION =============

def session_ok():

    hour = datetime.now().hour

    # ======== LONDON + NY ==========

    allowed = (

        7 <= hour <= 22
    )

    return allowed