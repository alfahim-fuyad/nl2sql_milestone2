import sqlite3


def execute_query(sql, db_path="data/database.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description] if cursor.description else []
    finally:
        conn.close()
    return cols, rows
