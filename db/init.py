import sqlite3
from pathlib import Path

DB_PATH = "chat.db"


# ===== 初始化資料庫 =====
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)

    # Messages table 存聊天紀錄
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,   -- 'user' or 'assistant'
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 存摘要紀錄(只存一筆)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summary (
            username TEXT PRIMARY KEY,
            summary_text TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 存 summary_pointer
    cursor.execute("""CREATE TABLE IF NOT EXISTS summary_pointer (
        username TEXT PRIMARY KEY,
        last_summarized_id INTEGER
    );""")    

    conn.commit()
    conn.close()

init_db()