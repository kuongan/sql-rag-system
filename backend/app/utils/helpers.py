import base64
import io
import json
import logging
from typing import Any, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

def encode_image_to_base64(image_buffer: io.BytesIO) -> str:
    """Convert image buffer to base64 string"""
    image_buffer.seek(0)
    image_base64 = base64.b64encode(image_buffer.getvalue()).decode('utf-8')
    return image_base64

def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Create standardized success response"""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }

def create_error_response(error: str, context: str = "") -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "success": False,
        "error": error,
        "context": context,
        "timestamp": datetime.utcnow().isoformat()
    }