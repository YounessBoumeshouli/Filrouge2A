from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
import hashlib
import uuid

app = Flask(__name__)
CORS(app)

# Simple in-memory storage (replace with database in production)
users_db = {}
sessions_db = {}

# Load existing users if file exists
USERS_FILE = "users.json"
if os.path.exists(USERS_FILE):
    try:
        with open(USERS_FILE, "r") as f:
            users_db = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users_db = {}


def save_users():
    """Save users to file"""
    with open(USERS_FILE, "w") as f:
        json.dump(users_db, f, indent=2)


def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token():
    """Generate a simple session token"""
    return str(uuid.uuid4())


@app.route("/api/auth/register", methods=["POST"])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["email", "password"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        email = data["email"].lower().strip()
        password = data["password"]
        name = data.get("name", email.split("@")[0])

        # Check if user already exists
        if email in users_db:
            return jsonify({"error": "User already exists"}), 409

        # Create new user
        user_id = str(uuid.uuid4())
        users_db[email] = {
            "id": user_id,
            "email": email,
            "name": name,
            "password": hash_password(password),
            "created_at": datetime.now().isoformat(),
            "is_active": True,
        }

        # Save to file
        save_users()

        # Create session
        token = generate_token()
        sessions_db[token] = {
            "user_id": user_id,
            "email": email,
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
        }

        return (
            jsonify(
                {
                    "success": True,
                    "message": "User registered successfully",
                    "user": {"id": user_id, "email": email, "name": name},
                    "token": token,
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/login", methods=["POST"])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()

        email = data.get("email", "").lower().strip()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Check if user exists
        if email not in users_db:
            return jsonify({"error": "Invalid credentials"}), 401

        user = users_db[email]

        # Check password
        if user["password"] != hash_password(password):
            return jsonify({"error": "Invalid credentials"}), 401

        # Check if user is active
        if not user.get("is_active", True):
            return jsonify({"error": "Account is deactivated"}), 401

        # Create session
        token = generate_token()
        sessions_db[token] = {
            "user_id": user["id"],
            "email": email,
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
        }

        return jsonify(
            {
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                },
                "token": token,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    """User logout endpoint"""
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if token in sessions_db:
            del sessions_db[token]

        return jsonify({"success": True, "message": "Logged out successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/me", methods=["GET"])
def get_current_user():
    """Get current user info"""
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not token or token not in sessions_db:
            return jsonify({"error": "Invalid or expired token"}), 401

        session = sessions_db[token]

        # Check if session is expired
        if datetime.fromisoformat(session["expires_at"]) < datetime.now():
            del sessions_db[token]
            return jsonify({"error": "Token expired"}), 401

        email = session["email"]
        if email not in users_db:
            return jsonify({"error": "User not found"}), 404

        user = users_db[email]

        return jsonify(
            {
                "success": True,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "created_at": user["created_at"],
                },
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/users", methods=["GET"])
def get_users():
    """Get all users (for admin/testing)"""
    try:
        users_list = []
        for email, user in users_db.items():
            users_list.append(
                {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "created_at": user["created_at"],
                    "is_active": user.get("is_active", True),
                }
            )

        return jsonify({"success": True, "users": users_list, "count": len(users_list)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "service": "auth-api",
            "port": 8001,
            "users_count": len(users_db),
            "active_sessions": len(sessions_db),
        }
    )


if __name__ == "__main__":
    print("Starting Authentication Server...")
    print("Available endpoints:")
    print("- POST http://localhost:8001/api/auth/register")
    print("- POST http://localhost:8001/api/auth/login")
    print("- POST http://localhost:8001/api/auth/logout")
    print("- GET  http://localhost:8001/api/auth/me")
    print("- GET  http://localhost:8001/api/auth/users")
    print("- GET  http://localhost:8001/api/health")
    app.run(host="0.0.0.0", port=8001, debug=True)
