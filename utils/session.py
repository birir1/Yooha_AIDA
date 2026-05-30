import uuid
from datetime import datetime

def generate_session_id():
    """
    Creates a timestamp-based session ID for analytics + memory tracking
    Format: YYYYMMDD_HHMMSS_shortuuid
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:6]
    return f"{timestamp}_{short_uuid}"