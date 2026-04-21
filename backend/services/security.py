from urllib.parse import urlparse

def is_safe_url(url: str) -> bool:
    """
    Validates a URL to prevent SSRF and block local file protocols.
    Only allows http and https protocols.
    """
    try:
        parsed = urlparse(url)
        # Must have a scheme and netloc
        if not parsed.scheme or not parsed.netloc:
            return False
            
        # Strictly allow only http and https
        if parsed.scheme.lower() not in ["http", "https"]:
            return False
            
        # Basic check to avoid internal/localhost routing tricks (optional, but good for zero-trust)
        # For a full implementation, you'd resolve the IP and ensure it's not in a private subnet,
        # but this simple check catches the most obvious malicious inputs.
        if parsed.netloc.lower() in ["localhost", "127.0.0.1", "0.0.0.0", "[::1]"]:
            return False
            
        return True
    except Exception:
        return False
