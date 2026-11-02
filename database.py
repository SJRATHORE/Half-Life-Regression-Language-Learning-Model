"""
database.py — SQLite schema + all query helpers for Farsi HLR
"""
import sqlite3
import os
import time
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'farsi_hlr.db')


# ── Connection ────────────────────────────────────────────────────────────────
def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Schema ────────────────────────────────────────────────────────────────────
def init_db():
    conn = get_conn()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS words (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            farsi            TEXT    NOT NULL,
            english          TEXT    NOT NULL,
            transliteration  TEXT    NOT NULL,
            category         TEXT    NOT NULL
        );

        /* One row per word — tracks exposure history */
        CREATE TABLE IF NOT EXISTS word_stats (
            word_id         INTEGER PRIMARY KEY,
            n_seen          INTEGER DEFAULT 0,
            n_correct       INTEGER DEFAULT 0,
            n_incorrect     INTEGER DEFAULT 0,
            last_seen_ts    REAL    DEFAULT 0,
            half_life_est   REAL    DEFAULT 1.0,
            next_review_ts  REAL    DEFAULT 0,
            FOREIGN KEY(word_id) REFERENCES words(id)
        );

        /* Append-only log — every practice event */
        CREATE TABLE IF NOT EXISTS reviews (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id      INTEGER NOT NULL,
            session_ts   REAL    NOT NULL,
            lag_days     REAL    NOT NULL,
            recall_rate  REAL    NOT NULL,
            p_hat        REAL    NOT NULL,
            h_hat        REAL    NOT NULL,
            was_correct  INTEGER NOT NULL,
            FOREIGN KEY(word_id) REFERENCES words(id)
        );

        /* Single global HLR weight vector + AdaGrad accumulators */
        CREATE TABLE IF NOT EXISTS hlr_weights (
            id               INTEGER PRIMARY KEY CHECK(id = 1),
            theta_bias       REAL DEFAULT  0.0,
            theta_n          REAL DEFAULT  0.5,
            theta_correct    REAL DEFAULT  0.5,
            theta_incorrect  REAL DEFAULT -0.5,
            accum_bias       REAL DEFAULT  0.0,
            accum_n          REAL DEFAULT  0.0,
            accum_correct    REAL DEFAULT  0.0,
            accum_incorrect  REAL DEFAULT  0.0
        );

        INSERT OR IGNORE INTO hlr_weights (id) VALUES (1);
    ''')
    conn.commit()
    conn.close()


# ── HLR weights ───────────────────────────────────────────────────────────────
def get_weights():
    conn = get_conn()
    r = conn.execute('SELECT * FROM hlr_weights WHERE id=1').fetchone()
    conn.close()
    theta = [r['theta_bias'], r['theta_n'], r['theta_correct'], r['theta_incorrect']]
    accum = [r['accum_bias'], r['accum_n'], r['accum_correct'], r['accum_incorrect']]
    return theta, accum


def save_weights(theta, accum):
    conn = get_conn()
    conn.execute('''
        UPDATE hlr_weights
        SET theta_bias=?, theta_n=?, theta_correct=?, theta_incorrect=?,
            accum_bias=?, accum_n=?,  accum_correct=?, accum_incorrect=?
        WHERE id=1
    ''', (*theta, *accum))
    conn.commit()
    conn.close()


# ── Word queries ──────────────────────────────────────────────────────────────
def get_due_words(limit=15):
    now = time.time()
    conn = get_conn()
    rows = conn.execute('''
        SELECT w.*, ws.n_seen, ws.n_correct, ws.n_incorrect,
               ws.last_seen_ts, ws.half_life_est, ws.next_review_ts
        FROM words w
        JOIN word_stats ws ON w.id = ws.word_id
        WHERE ws.next_review_ts <= ? AND ws.n_seen > 0
        ORDER BY ws.next_review_ts ASC
        LIMIT ?
    ''', (now, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_new_words(limit=10):
    conn = get_conn()
    rows = conn.execute('''
        SELECT w.*, ws.n_seen, ws.n_correct, ws.n_incorrect,
               ws.last_seen_ts, ws.half_life_est, ws.next_review_ts
        FROM words w
        JOIN word_stats ws ON w.id = ws.word_id
        WHERE ws.n_seen = 0
        ORDER BY w.id ASC
        LIMIT ?
    ''', (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_word_by_id(word_id):
    conn = get_conn()
    row = conn.execute('''
        SELECT w.*, ws.n_seen, ws.n_correct, ws.n_incorrect,
               ws.last_seen_ts, ws.half_life_est, ws.next_review_ts
        FROM words w
        JOIN word_stats ws ON w.id = ws.word_id
        WHERE w.id = ?
    ''', (word_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_words():
    conn = get_conn()
    rows = conn.execute('''
        SELECT w.*, ws.n_seen, ws.n_correct, ws.n_incorrect,
               ws.half_life_est, ws.next_review_ts, ws.last_seen_ts
        FROM words w
        JOIN word_stats ws ON w.id = ws.word_id
        ORDER BY w.category, w.id
    ''').fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Write operations ──────────────────────────────────────────────────────────
def update_word_stats(word_id, n_seen, n_correct, n_incorrect,
                      last_seen_ts, half_life_est, next_review_ts):
    conn = get_conn()
    conn.execute('''
        UPDATE word_stats
        SET n_seen=?, n_correct=?, n_incorrect=?,
            last_seen_ts=?, half_life_est=?, next_review_ts=?
        WHERE word_id=?
    ''', (n_seen, n_correct, n_incorrect,
          last_seen_ts, half_life_est, next_review_ts, word_id))
    conn.commit()
    conn.close()


def insert_review(word_id, session_ts, lag_days, recall_rate, p_hat, h_hat, was_correct):
    conn = get_conn()
    conn.execute('''
        INSERT INTO reviews
            (word_id, session_ts, lag_days, recall_rate, p_hat, h_hat, was_correct)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (word_id, session_ts, lag_days, recall_rate, p_hat, h_hat, was_correct))
    conn.commit()
    conn.close()


# ── Dashboard stats ───────────────────────────────────────────────────────────
def get_dashboard_stats():
    conn  = get_conn()
    now   = time.time()

    total   = conn.execute('SELECT COUNT(*) FROM words').fetchone()[0]
    seen    = conn.execute(
        'SELECT COUNT(*) FROM word_stats WHERE n_seen > 0').fetchone()[0]
    due     = conn.execute(
        'SELECT COUNT(*) FROM word_stats WHERE next_review_ts <= ? AND n_seen > 0',
        (now,)).fetchone()[0]
    avg_row = conn.execute('''
        SELECT AVG(recall_rate) FROM (
            SELECT recall_rate FROM reviews ORDER BY session_ts DESC LIMIT 200
        )''').fetchone()[0]
    avg_recall = round((avg_row or 0) * 100, 1)
    streak = _compute_streak(conn)
    conn.close()

    return {
        'total':      total,
        'seen':       seen,
        'unseen':     total - seen,
        'due':        due,
        'avg_recall': avg_recall,
        'streak':     streak,
    }


def _compute_streak(conn):
    rows = conn.execute('''
        SELECT DISTINCT date(session_ts, 'unixepoch', 'localtime') AS day
        FROM reviews ORDER BY day DESC
    ''').fetchall()
    if not rows:
        return 0
    today    = date.today()
    streak   = 0
    expected = today
    for row in rows:
        day = date.fromisoformat(row[0])
        if day == expected:
            streak   += 1
            expected -= timedelta(days=1)
        elif streak == 0 and day == today - timedelta(days=1):
            streak   += 1
            expected  = day - timedelta(days=1)
        else:
            break
    return streak


# ── Progress data (for charts) ────────────────────────────────────────────────
def get_progress_data():
    conn = get_conn()

    daily = conn.execute('''
        SELECT date(session_ts, 'unixepoch', 'localtime') AS day,
               ROUND(AVG(recall_rate)*100, 1)              AS avg_recall,
               COUNT(*)                                     AS n_reviews
        FROM reviews
        GROUP BY day ORDER BY day
    ''').fetchall()

    half_lives = conn.execute('''
        SELECT half_life_est FROM word_stats WHERE n_seen > 0
    ''').fetchall()

    per_category = conn.execute('''
        SELECT w.category,
               COUNT(*)                             AS total,
               SUM(CASE WHEN ws.n_seen>0 THEN 1 ELSE 0 END) AS seen,
               ROUND(AVG(ws.half_life_est),2)       AS avg_hl
        FROM words w JOIN word_stats ws ON w.id=ws.word_id
        GROUP BY w.category
    ''').fetchall()

    # Cumulative unique words seen per day
    cum = conn.execute('''
        SELECT date(session_ts, 'unixepoch', 'localtime') AS day,
               COUNT(DISTINCT word_id) AS new_words
        FROM reviews
        GROUP BY day ORDER BY day
    ''').fetchall()

    conn.close()
    return {
        'daily':        [dict(r) for r in daily],
        'half_lives':   [r[0] for r in half_lives],
        'per_category': [dict(r) for r in per_category],
        'cumulative':   [dict(r) for r in cum],
    }
