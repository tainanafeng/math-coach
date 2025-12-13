# ===== 基本 CRUD：聊天紀錄 =====
# 將來換成 MySQL 或 Postgres → CRUD 層改掉即可，不動主程式

import sqlite3
import time
from pathlib import Path

DB_PATH = "chat.db"

# -------- SQLite 安全寫入(自動重試) -------- #
def safe_sqlite_call(func, retries=3, delay=0.1):
    """
    - 專門處理 SQLite locked 問題
    - locked 時自動等待 & 重試
    - 其他錯誤一律往外丟（你會看到錯誤訊息）
    """
    for attempt in range(retries):
        try:
            return func()
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                # SQLite 被鎖住 → 等一下再試
                time.sleep(delay)
                continue
            else:
                # 不是 locked 的錯誤 → 直接拋出
                raise

    raise sqlite3.OperationalError("Database kept locked after retries.")


# -------- 讀取聊天紀錄(前端用) -------- #
def load_messages(username):

    def _read():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT role, content FROM messages WHERE username=? ORDER BY id",
            (username,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    rows = safe_sqlite_call(_read)

    return [{"role": r[0], "content": r[1]} for r in rows]


# -------- 寫入訊息(自動 retry 保證成功) -------- #
def save_message(username, role, content):

    def _write():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO messages (username, role, content) VALUES (?, ?, ?)",
            (username, role, content)
        )
        conn.commit()
        conn.close()

    safe_sqlite_call(_write)


# -------- 讀取最後 N 則對話(model用) -------- #
def load_recent_messages(username, n=20):

    def _read():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT role, content FROM messages
            WHERE username=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (username, n)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    rows = safe_sqlite_call(_read)

    rows.reverse()  # 由舊到新排序
    return [{"role": r[0], "content": r[1]} for r in rows]
