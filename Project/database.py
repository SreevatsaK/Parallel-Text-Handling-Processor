import sqlite3
import csv
import json
import threading
from datetime import datetime

DB_NAME = "data/text_processing.db"

_db_lock = threading.Lock()


# ──────────────────────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────────────────────

def _get_conn() -> sqlite3.Connection:
    """Open a WAL-mode connection with a generous busy timeout."""
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")   # wait up to 5 s before raising
    return conn


# ──────────────────────────────────────────────────────────────
#  INIT
# ──────────────────────────────────────────────────────────────

def create_database(reset: bool = True):
    
    with _db_lock:
        conn   = _get_conn()
        cursor = conn.cursor()

        if reset:
            cursor.execute("DROP TABLE IF EXISTS processed_articles")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_articles (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            text_chunk       TEXT,
            sentiment_score  INTEGER,
            sentiment_label  TEXT,
            keyword_count    INTEGER,
            keywords         TEXT,
            positive_words   TEXT,
            negative_words   TEXT,
            word_frequencies TEXT,
            tags             TEXT,
            timestamp        TEXT
        )
        """)

        # Indexes for fast search / filter
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment ON processed_articles(sentiment_label)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_score     ON processed_articles(sentiment_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_keywords  ON processed_articles(keywords)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags      ON processed_articles(tags)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_time      ON processed_articles(timestamp)")

        conn.commit()
        conn.close()


# ──────────────────────────────────────────────────────────────
#  INSERT  (thread-safe)
# ──────────────────────────────────────────────────────────────

def insert_articles_batch(articles: list[dict]):
   
    if not articles:
        return

    ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []

    for article in articles:
        text     = article.get("text", "")
        analysis = article.get("analysis", {})
        rows.append((
            text,
            analysis.get("sentiment_score", 0),
            analysis.get("sentiment_label", "Neutral"),
            analysis.get("keyword_count",   0),
            ",".join(analysis.get("keywords",       [])),
            ",".join(analysis.get("positive_words", [])),
            ",".join(analysis.get("negative_words", [])),
            json.dumps(analysis.get("word_frequencies", {})),
            ",".join(analysis.get("themes", ["General"])),
            ts
        ))

    with _db_lock:                          # ← serialise writes
        conn   = _get_conn()
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO processed_articles
                (text_chunk, sentiment_score, sentiment_label, keyword_count,
                 keywords, positive_words, negative_words, word_frequencies,
                 tags, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows)
        conn.commit()
        conn.close()


# ──────────────────────────────────────────────────────────────
#  QUERY HELPERS
# ──────────────────────────────────────────────────────────────

def get_summary() -> dict:
    conn = _get_conn()
    cur  = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM processed_articles")
    total = cur.fetchone()[0]

    cur.execute("SELECT AVG(sentiment_score) FROM processed_articles")
    avg = cur.fetchone()[0] or 0

    cur.execute("SELECT sentiment_label, COUNT(*) FROM processed_articles GROUP BY sentiment_label")
    sentiment_dist = cur.fetchall()

    cur.execute("SELECT tags, COUNT(*) FROM processed_articles GROUP BY tags")
    theme_dist = cur.fetchall()

    conn.close()
    return {
        "total":          total,
        "avg_score":      round(avg, 2),
        "sentiment_dist": sentiment_dist,
        "theme_dist":     theme_dist
    }


def search_articles(keyword: str = "", min_score: int = None,
                    max_score: int = None, limit: int = 200) -> list:
    conn   = _get_conn()
    cur    = conn.cursor()

    query  = "SELECT text_chunk, keywords, sentiment_label, sentiment_score FROM processed_articles WHERE 1=1"
    params = []

    if keyword:
        query  += " AND (text_chunk LIKE ? OR keywords LIKE ?)"
        params += [f"%{keyword}%", f"%{keyword}%"]

    if min_score is not None:
        query  += " AND sentiment_score >= ?"
        params.append(min_score)

    if max_score is not None:
        query  += " AND sentiment_score <= ?"
        params.append(max_score)

    query += f" LIMIT {limit}"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


# ──────────────────────────────────────────────────────────────
#  EXPORT
# ──────────────────────────────────────────────────────────────

def export_to_csv(path: str = "data/exported_results.csv"):
    conn   = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM processed_articles")
    rows   = cursor.fetchall()
    conn.close()

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "text_chunk", "sentiment_score", "sentiment_label",
            "keyword_count", "keywords", "positive_words", "negative_words",
            "word_frequencies", "tags", "timestamp"
        ])
        writer.writerows(rows)

    return path
