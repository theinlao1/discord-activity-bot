import sqlite3

DB_PATH = 'data/activity.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute(
            '''CREATE TABLE IF NOT EXISTS activity(
                    user_id         INTEGER PRIMARY KEY,
                    username        TEXT,
                    messages        INTEGER DEFAULT 0,
                    voice_minutes   INTEGER DEFAULT 0)
            '''
        )
        conn.commit()

def add_messages(user_id: int, username: str):
    with get_conn() as conn:
        conn.execute(
            '''INSERT INTO activity (user_id, username, messages)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id) DO UPDATE SET
                    messages = messages + 1,
                    username = ?
        ''', (user_id, username, username))
        conn.commit()

def add_voice_minutes(user_id: int, username: str, minutes: int):
    with get_conn() as conn:
        conn.execute('''
            INSERT INTO activity (user_id, username, voice_minutes)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                voice_minutes = voice_minutes + ?,
                username = ?
        ''', (user_id, username, minutes, minutes, username))
        conn.commit()

def get_top_users(limit: int = 5):
    with get_conn() as conn:
        cursor = conn.execute('''
            SELECT username, messages, voice_minutes,
                   (messages + voice_minutes * 2) as score
            FROM activity
            ORDER BY score DESC
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

def reset_status():
    with get_conn() as conn:
        conn.execute('DELETE FROM activity')
        conn.commit()
