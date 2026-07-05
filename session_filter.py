from datetime import datetime
from config import *

# =========== LONDON + NY SESSION =============

def session_ok():
    """Check if current time is within trading session"""
    
    hour = datetime.now().hour
    
    # London Session (7-10 AM GMT)
    london_session = LONDON_START <= hour <= LONDON_END
    
    # NY Session (1-5 PM GMT)
    ny_session = NY_START <= hour <= NY_END
    
    allowed = london_session or ny_session
    
    if not allowed:
        print(f"⏰ Current hour: {hour} (London: {LONDON_START}-{LONDON_END}, NY: {NY_START}-{NY_END})")
    
    return allowed