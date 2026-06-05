from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.environ.get("DB_PATH", "/data/albums.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS albums (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            year INTEGER NOT NULL,
            genre TEXT NOT NULL,
            label TEXT,
            rating INTEGER DEFAULT 0
        )
    """)
    # Seed data if empty
    cursor.execute("SELECT COUNT(*) FROM albums")
    if cursor.fetchone()[0] == 0:
        seed = [
            ("Reign in Blood", "Slayer", 1986, "thrash", "Def Jam", 10),
            ("Master of Puppets", "Metallica", 1986, "thrash", "Elektra", 10),
            ("Rust in Peace", "Megadeth", 1990, "thrash", "Capitol", 10),
            ("Among the Living", "Anthrax", 1987, "thrash", "Island", 9),
            ("Beneath the Remains", "Sepultura", 1989, "thrash", "Roadracer", 9),
            ("Persecution Mania", "Sodom", 1987, "thrash", "Steamhammer", 9),
            ("Agent Orange", "Sodom", 1989, "thrash", "Steamhammer", 10),
            ("Terrible Certainty", "Kreator", 1987, "thrash", "Noise", 9),
            ("Pleasure to Kill", "Kreator", 1986, "thrash", "Noise", 10),
            ("Darkness Descends", "Dark Angel", 1986, "thrash", "Combat", 9),
            ("Scream Bloody Gore", "Death", 1987, "death", "Combat", 10),
            ("Leprosy", "Death", 1988, "death", "Combat", 10),
            ("Altars of Madness", "Morbid Angel", 1989, "death", "Earache", 10),
            ("Slowly We Rot", "Obituary", 1989, "death", "Roadracer", 9),
            ("Cause of Death", "Obituary", 1990, "death", "Roadracer", 10),
            ("Left Hand Path", "Entombed", 1990, "death", "Earache", 10),
            ("Like an Ever Flowing Stream", "Dismember", 1991, "death", "Nuclear Blast", 10),
            ("The IVth Crusade", "Bolt Thrower", 1992, "death", "Earache", 9),
            ("Effigy of the Forgotten", "Suffocation", 1991, "death", "Roadracer", 10),
            ("Human", "Death", 1991, "death", "Relativity", 10),
        ]
        cursor.executemany(
            "INSERT INTO albums (title, artist, year, genre, label, rating) VALUES (?,?,?,?,?,?)",
            seed
        )
    conn.commit()
    conn.close()

@app.route("/api/albums", methods=["GET"])
def get_albums():
    genre = request.args.get("genre")
    conn = get_db()
    if genre:
        rows = conn.execute("SELECT * FROM albums WHERE genre=? ORDER BY year", (genre,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM albums ORDER BY genre, year").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/albums/<int:album_id>", methods=["GET"])
def get_album(album_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM albums WHERE id=?", (album_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "Not found"}), 404
    return jsonify(dict(row))

@app.route("/api/albums", methods=["POST"])
def add_album():
    data = request.get_json()
    required = ["title", "artist", "year", "genre"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO albums (title, artist, year, genre, label, rating) VALUES (?,?,?,?,?,?)",
        (data["title"], data["artist"], data["year"], data["genre"],
         data.get("label", ""), data.get("rating", 0))
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": new_id, "message": "Album added"}), 201

@app.route("/api/albums/<int:album_id>", methods=["DELETE"])
def delete_album(album_id):
    conn = get_db()
    conn.execute("DELETE FROM albums WHERE id=?", (album_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted"})

@app.route("/api/stats", methods=["GET"])
def get_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM albums").fetchone()[0]
    thrash = conn.execute("SELECT COUNT(*) FROM albums WHERE genre='thrash'").fetchone()[0]
    death = conn.execute("SELECT COUNT(*) FROM albums WHERE genre='death'").fetchone()[0]
    conn.close()
    return jsonify({"total": total, "thrash": thrash, "death": death})

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
