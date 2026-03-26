import uuid
from flask import Blueprint, jsonify, request, g
from database.db import get_db_connection, release_db_connection
from middleware.auth_middleware import token_required

session_bp = Blueprint("sessions", __name__)


@session_bp.route("/sessions", methods=["POST"])
@token_required
def create_session():
    """Create a fresh empty session for the authenticated user."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO ai_sessions (user_id) VALUES (%s) RETURNING id, created_at",
            (g.user.id,)
        )
        created = cur.fetchone()
        conn.commit()
        return jsonify({"id": str(created[0]), "created_at": created[1].isoformat()}), 201
    except Exception:
        conn.rollback()
        return jsonify({"error": "Failed to create session."}), 500
    finally:
        cur.close()
        release_db_connection(conn)


@session_bp.route("/sessions", methods=["GET"])
@token_required
def get_sessions():
    """Return the 50 most recent sessions (paginated with offset support)."""
    try:
        offset = int(request.args.get("offset", 0))
    except ValueError:
        offset = 0

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, created_at FROM ai_sessions WHERE user_id = %s ORDER BY created_at DESC LIMIT 50 OFFSET %s",
            (g.user.id, offset)
        )
        sessions = cur.fetchall()
    finally:
        cur.close()
        release_db_connection(conn)

    return jsonify([{"id": str(s[0]), "created_at": s[1].isoformat()} for s in sessions])


@session_bp.route("/sessions/<session_id>/messages", methods=["GET"])
@token_required
def get_messages(session_id):
    """Return all messages belonging to a session."""
    # Validate UUID before hitting the database — Postgres raises DataError on bad castes.
    try:
        validated_id = uuid.UUID(session_id)
    except (ValueError, AttributeError):
        return jsonify({"error": "Invalid session ID format."}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # First verify the session belongs to the user
        cur.execute("SELECT id FROM ai_sessions WHERE id = %s AND user_id = %s", (str(validated_id), g.user.id))
        if not cur.fetchone():
            return jsonify({"error": "Session not found or unauthorized."}), 404

        cur.execute(
            "SELECT id, role, content, created_at FROM ai_messages WHERE session_id = %s ORDER BY created_at ASC",
            (str(validated_id),)
        )
        messages = cur.fetchall()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        release_db_connection(conn)

    return jsonify([
        {"id": m[0], "role": m[1], "content": m[2], "created_at": m[3].isoformat()}
        for m in messages
    ])


@session_bp.route("/sessions/<session_id>", methods=["DELETE"])
@token_required
def delete_session(session_id):
    """Delete a session owned by the authenticated user."""
    try:
        validated_id = uuid.UUID(session_id)
    except (ValueError, AttributeError):
        return jsonify({"error": "Invalid session ID format."}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id FROM ai_sessions WHERE id = %s AND user_id = %s",
            (str(validated_id), g.user.id)
        )
        if not cur.fetchone():
            return jsonify({"error": "Session not found or unauthorized."}), 404

        cur.execute("DELETE FROM ai_sessions WHERE id = %s", (str(validated_id),))
        conn.commit()
        return jsonify({"status": "deleted", "id": str(validated_id)}), 200
    except Exception:
        conn.rollback()
        return jsonify({"error": "Failed to delete session."}), 500
    finally:
        cur.close()
        release_db_connection(conn)