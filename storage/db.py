import sqlite3
import json
import os
from datetime import datetime
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Table for harvested OSINT intelligence posts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS intel_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_type TEXT NOT NULL,          -- RSS, TWITTER, TIKTOK, TELEGRAM, WEB
        source_name TEXT NOT NULL,
        author TEXT,
        url TEXT UNIQUE,
        title TEXT,
        content TEXT NOT NULL,
        publish_time TEXT,
        category TEXT,
        score REAL DEFAULT 0.0,
        score_breakdown TEXT,              -- JSON breakdown of score components
        harvest_iteration INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table for extracted OSINT entities (locations, dates, keywords, usernames)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS intel_entities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        entity_type TEXT NOT NULL,         -- LOCATION, DATE, KEYWORD, HANDLE
        entity_value TEXT NOT NULL,
        confidence REAL DEFAULT 1.0,
        FOREIGN KEY(post_id) REFERENCES intel_posts(id)
    );
    """)

    # Table for Agent Loop iteration histories and overall scores
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_iterations (
        iteration INTEGER PRIMARY KEY,
        posts_harvested INTEGER,
        avg_score REAL,
        max_score REAL,
        query_keywords TEXT,
        status TEXT,                       -- IN_PROGRESS, THRESHOLD_REACHED, REFINING
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table for compiled intelligence summary reports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS intelligence_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        overall_score REAL NOT NULL,
        total_sources INTEGER,
        pre_event_signals_count INTEGER,
        key_findings TEXT,                 -- JSON array of findings
        executive_summary TEXT,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
    print(f"[DB] Initialized CeutaOSINT database schema at: {DB_PATH}")

def save_post(post_data):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        score_breakdown_json = json.dumps(post_data.get("score_breakdown", {}))
        cursor.execute("""
        INSERT OR REPLACE INTO intel_posts (source_type, source_name, author, url, title, content, publish_time, category, score, score_breakdown, harvest_iteration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post_data.get("source_type", "WEB"),
            post_data.get("source_name", "Unknown"),
            post_data.get("author", "Anonymous"),
            post_data.get("url"),
            post_data.get("title", ""),
            post_data.get("content", ""),
            post_data.get("publish_time", datetime.now().isoformat()),
            post_data.get("category", "UNASSIGNED"),
            post_data.get("score", 0.0),
            score_breakdown_json,
            post_data.get("harvest_iteration", 1)
        ))
        post_id = cursor.lastrowid
        conn.commit()

        # Save extracted entities if present
        for ent in post_data.get("entities", []):
            cursor.execute("""
            INSERT INTO intel_entities (post_id, entity_type, entity_value, confidence)
            VALUES (?, ?, ?, ?)
            """, (post_id, ent.get("type", "KEYWORD"), ent.get("value", ""), ent.get("confidence", 1.0)))
        conn.commit()
        return post_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_all_posts(start_date=None, end_date=None, category=None, source_type=None, search_text=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM intel_posts WHERE 1=1"
    params = []

    if start_date:
        # Include full day starting at 00:00:00
        if len(start_date) == 10:
            start_date_param = f"{start_date}T00:00:00"
        else:
            start_date_param = start_date
        query += " AND publish_time >= ?"
        params.append(start_date_param)

    if end_date:
        # Include full day ending at 23:59:59
        if len(end_date) == 10:
            end_date_param = f"{end_date}T23:59:59"
        else:
            end_date_param = end_date
        query += " AND publish_time <= ?"
        params.append(end_date_param)

    if category:
        query += " AND category = ?"
        params.append(category)

    if source_type:
        query += " AND source_type = ?"
        params.append(source_type)

    if search_text and search_text.strip():
        term = f"%{search_text.strip()}%"
        query += " AND (title LIKE ? OR content LIKE ? OR author LIKE ? OR source_name LIKE ?)"
        params.extend([term, term, term, term])

    query += " ORDER BY score DESC, id DESC"
    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # Parse JSON score breakdown
    for r in rows:
        if r.get("score_breakdown"):
            try:
                r["score_breakdown"] = json.loads(r["score_breakdown"])
            except Exception:
                pass
    return rows

def log_iteration(iteration, posts_count, avg_score, max_score, keywords, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO agent_iterations (iteration, posts_harvested, avg_score, max_score, query_keywords, status)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (iteration, posts_count, avg_score, max_score, json.dumps(keywords), status))
    conn.commit()
    conn.close()

def get_iterations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agent_iterations ORDER BY iteration ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    for r in rows:
        if r.get("query_keywords"):
            try:
                r["query_keywords"] = json.loads(r["query_keywords"])
            except Exception:
                pass
    return rows

if __name__ == "__main__":
    init_db()
