import sqlite3
import random
from typing import Tuple
from db_paths import db_paths

conn = sqlite3.connect(db_paths['statham'])
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS statham_quotes
                  (id INTEGER PRIMARY KEY, photo_id TEXT, caption TEXT)''')


def get_max_id():
    cursor.execute("SELECT MAX(id) FROM statham_quotes")
    max_id = cursor.fetchone()
    if max_id is not None:
        return max_id[0]
    return None


def get_randQuote():
    max_id = get_max_id()
    if max_id is None:
        return None
    random_number = random.randint(1, max_id)
    cursor.execute("SELECT photo_id FROM statham_quotes WHERE id=?", (random_number,))
    photo_id = cursor.fetchone()
    cursor.execute("SELECT caption FROM statham_quotes WHERE id=?", (random_number,))
    caption = cursor.fetchone()
    photo = None
    txt = None
    if photo_id is not None:
        photo = photo_id[0]
    if caption is not None:
        txt = caption[0]
    return (photo, txt)


def insert_quote(photo=None, caption=None):
    max_id = get_max_id()
    if max_id is None:
        max_id = 0
    if photo is None and caption is None:
        return
    cursor.execute("INSERT INTO statham_quotes (id, photo_id, caption) VALUES (?, ?, ?)", (max_id + 1, photo, caption,))
    conn.commit()


def del_quote(id):
    cursor.execute("DELETE FROM statham_quotes WHERE id=?", (id,))
    conn.commit()
    if cursor.rowcount == 0:
        return 0
    try:
        for i in range(id + 1, get_max_id() + 1):
            cursor.execute("UPDATE statham_quotes SET id=? WHERE id=?", (i - 1, i,))
    except Exception:
        pass
    if cursor.rowcount == 0:
        return 0
    return 1


def get_statham_db():
    cursor.execute("SELECT * FROM statham_quotes")
    rows = cursor.fetchall()
    return rows


if __name__ == '__main__':
    print(get_statham_db())
