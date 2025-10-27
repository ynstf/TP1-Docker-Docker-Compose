from flask import Flask, request, jsonify
import psycopg2
import redis
import os

app = Flask(__name__)

# DB config (unchanged)
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "mydb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mypassword")

# Redis config (unchanged)
REDIS_HOST = os.getenv("REDIS_HOST", "redis_cache")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    email = data.get("email")

    if not username or not email:
        return jsonify({"error": "Missing username or email"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id",
        (username, email)
    )
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    # cache in Redis
    r.set(f"user:{user_id}", f"{username}:{email}")

    return jsonify({"id": user_id, "username": username, "email": email}), 201

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    # Check Redis cache first
    cached = r.get(f"user:{user_id}")
    if cached:
        username, email = cached.decode().split(":", 1)
        return jsonify({"id": user_id, "username": username, "email": email, "cached": True})

    # Else fetch from DB
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, email FROM users WHERE id=%s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        username, email = row
        # cache in Redis
        r.set(f"user:{user_id}", f"{username}:{email}")
        return jsonify({"id": user_id, "username": username, "email": email, "cached": False})
    else:
        return jsonify({"error": "User not found"}), 404

@app.route("/users", methods=["GET"])
def list_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email FROM users")
    users = [{"id": row[0], "username": row[1], "email": row[2]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(users)

# -------------------
# New: update (PUT)
# -------------------
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json or {}
    username = data.get("username")
    email = data.get("email")

    # If neither provided, nothing to update
    if username is None and email is None:
        return jsonify({"error": "No fields to update"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # Build update dynamically but keep params safe
    fields = []
    params = []
    if username is not None:
        fields.append("username = %s")
        params.append(username)
    if email is not None:
        fields.append("email = %s")
        params.append(email)
    params.append(user_id)

    cur.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = %s RETURNING id, username, email", tuple(params))
    row = cur.fetchone()
    if not row:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404

    conn.commit()
    cur.close()
    conn.close()

    # Invalidate and refresh cache
    r.delete(f"user:{user_id}")
    r.set(f"user:{user_id}", f"{row[1]}:{row[2]}")

    return jsonify({"id": row[0], "username": row[1], "email": row[2]})

# -------------------
# New: delete (DELETE)
# -------------------
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s RETURNING id", (user_id,))
    row = cur.fetchone()
    if not row:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404

    conn.commit()
    cur.close()
    conn.close()

    # Remove from cache
    r.delete(f"user:{user_id}")

    return jsonify({"message": f"User {user_id} deleted"})

# -------------------
# New: health endpoint
# -------------------
@app.route("/health", methods=["GET"])
def health():
    status = {"db": "unknown", "redis": "unknown"}
    # check postgres
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        ok = cur.fetchone()
        cur.close()
        conn.close()
        status["db"] = "ok" if ok and ok[0] == 1 else "fail"
    except Exception as e:
        status["db"] = f"error: {str(e)}"

    # check redis
    try:
        status["redis"] = "ok" if r.ping() else "fail"
    except Exception as e:
        status["redis"] = f"error: {str(e)}"

    return jsonify(status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
