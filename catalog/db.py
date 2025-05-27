# catalog/db.py
import sqlite3

def get_all_images():
    conn = sqlite3.connect('catalog.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM images ORDER BY filename")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]
