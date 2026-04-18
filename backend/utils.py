import logging

logger = logging.getLogger(__name__)

def map_error_to_friendly_message(error: Exception) -> str:
    """
    Maps technical exceptions (like API errors) to user-friendly strings.
    """
    err_str = str(error)
    
    # Custom encryption error
    if "password protected" in err_str.lower() or "encrypted" in err_str.lower():
        return "PDF_PASSWORD_REQUIRED"
    
    # Check for Google API specific errors
    if "503" in err_str and "UNAVAILABLE" in err_str:
        return "The AI engine is currently experiencing high demand. Please try again in a few moments."
    
    if "429" in err_str:
        return "Too many requests. Please wait a minute before retrying."
    
    if "400" in err_str:
        return "The document format or content couldn't be processed. Please ensure it's a clear image or PDF."
        
    if "401" in err_str or "403" in err_str:
        return "Internal authentication issue. Please contact support."

    # Fallback to a polite generic message if it looks too technical
    if "{" in err_str or "code:" in err_str or "Error" in err_str:
        return "An unexpected error occurred while analyzing this document. Please re-upload or try again later."
        
    return err_str
