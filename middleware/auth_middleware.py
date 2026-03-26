from functools import wraps
from flask import request, jsonify, g
from supabase_client import supabase


def _extract_bearer_token(auth_header):
    """Safely parse Bearer token from Authorization header."""
    if not auth_header:
        return None
    parts = auth_header.strip().split()
    if len(parts) != 2 or parts[0].lower() != 'bearer' or not parts[1].strip():
        return None
    return parts[1].strip()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        token = _extract_bearer_token(auth_header)
        if not token:
            return jsonify({"error": "Invalid or missing Authorization header"}), 401
        
        try:
            res = supabase.auth.get_user(token)
            
            if not res.user:
                return jsonify({"error": "Invalid or expired token"}), 401
                
            g.user = res.user
        except Exception:
            return jsonify({"error": "Authentication failed"}), 401
            
        return f(*args, **kwargs)
    
    return decorated
