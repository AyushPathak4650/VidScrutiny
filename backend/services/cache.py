import sqlite3
import json
import os
from typing import Optional, Dict, Any

# Ensure database is stored in the persistent temp_files directory
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "temp_files", "vidscrutiny_cache.db")

def init_db():
    """Initializes the SQLite database table for caching video analyses."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_cache (
            url TEXT PRIMARY KEY,
            fact_checks JSON,
            stream_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_cached_analysis(url: str) -> Optional[Dict[str, Any]]:
    """Retrieves a cached analysis for a given URL, if it exists."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT fact_checks, stream_url FROM video_cache WHERE url = ?", (url,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "fact_checks": json.loads(row[0]),
                "stream_url": row[1]
            }
        return None
    except Exception as e:
        print(f"Cache read error: {e}")
        return None

def save_analysis(url: str, fact_checks: list, stream_url: str):
    """Saves the analysis results to the SQLite cache."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO video_cache (url, fact_checks, stream_url) VALUES (?, ?, ?)",
            (url, json.dumps(fact_checks), stream_url)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Cache write error: {e}")

# Initialize the database when this module is imported
init_db()
