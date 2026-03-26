# Main entry point of the Flask app
import os
from flask import Flask, render_template, jsonify, request, g
from routes.analyze_routes import analyze_bp
from routes.session_routes import session_bp
from supabase_client import supabase  
from database.db import initialize_database
from middleware.auth_middleware import token_required
try:
    from supabase_auth.errors import AuthApiError
except ImportError:
    # Fallback for different supabase package versions
    AuthApiError = Exception

app = Flask(__name__)

# Ensure required Postgres tables/extensions exist before serving requests.
initialize_database()

# Security & reliability config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# Block uploads larger than 16 MB to prevent DoS via large file attacks.
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Register blueprints
app.register_blueprint(analyze_bp)
app.register_blueprint(session_bp)

# Handle 413 (file too large) gracefully instead of crashing
@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({"error": "File is too large. Maximum upload size is 16 MB."}), 413

@app.route('/')
def index():
    """Serve the landing page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Serve the dashboard page"""
    return render_template('dashboard.html')


@app.route('/pest-detection')
def pest_detection():
    """Serve the pest detection page"""
    return render_template('pest-detection.html')

@app.route('/crop-advisory')
def crop_advisory():
    """Serve the crop advisory page"""
    return render_template('crop-advisory.html')

@app.route('/login')
def login_page():
    """Serve the login page"""
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    """Serve the signup page"""
    return render_template('signup.html')

# 1. Signup API
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required."}), 400
    try:
        res = supabase.auth.sign_up({
            "email": data["email"],
            "password": data["password"],
            "options": {
                "data": {
                    "name": data.get("name", "")
                }
            }
        })
        return jsonify({"message": "User created"})
    except AuthApiError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Signup failed. Please try again."}), 500


# 2. Login API
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required."}), 400
    try:
        res = supabase.auth.sign_in_with_password({
            "email": data["email"],
            "password": data["password"]
        })
        # Fetch the user's name from auth metadata instead of a profiles table
        user_meta = res.user.user_metadata or {}
        user_name = user_meta.get("name") or user_meta.get("full_name") or data["email"]
        
        return jsonify({
            "access_token": res.session.access_token,
            "user": res.user.id,
            "name": user_name,
            "email": res.user.email
        })
    except AuthApiError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Login failed. Please try again."}), 500

# 3. Create Chat
@app.route("/create-chat", methods=["POST"])
@token_required
def create_chat():
    data = request.json

    res = supabase.table("chats").insert({
        "user_id": g.user.id,
        "title": data.get("title", "New Chat")
    }).execute()

    return jsonify(res.data)

# 4. Send Message
@app.route("/send-message", methods=["POST"])
@token_required
def send_message():
    data = request.json

    supabase.table("messages").insert({
        "chat_id": data["chat_id"],
        "role": "user",
        "content": data["message"]
    }).execute()

    return jsonify({"status": "saved"})


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)