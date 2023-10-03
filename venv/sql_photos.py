import datetime
import sqlite3
import json
from typing import Dict

conn = sqlite3.connect('slutsDB.db')
cursor = conn.cursor()

# Creating a table with id and info columns
cursor.execute('''CREATE TABLE IF NOT EXISTS sluts_info 
                  (id INTEGER PRIMARY KEY, note TEXT, votes TEXT, file_id TEXT, origin TEXT)''')


def get_last():
    cursor.execute("SELECT MAX(id) FROM sluts_info")
    rows = cursor.fetchone()[0]
    if rows is None:
        return 0
    return rows


def add_photo_id(num, file_id, username):
    cursor.execute("INSERT INTO sluts_info (id, file_id, origin) VALUES (?, ?, ?)", (num, file_id, username))
    conn.commit()


def add_rate(num, username, rate):
    cursor.execute("SELECT votes FROM sluts_info WHERE id=?", (num,))
    rows = cursor.fetchone()[0]
    votes = {} if rows is None else json.loads(rows)
    votes[username] = rate
    votes = json.dumps(votes)
    cursor.execute("UPDATE sluts_info SET votes=? WHERE id=?", (votes, num,))
    conn.commit()


def add_note(num, note):
    cursor.execute("UPDATE sluts_info SET note=? WHERE id=?", (note, num,))
    conn.commit()


def get_note_sql(num):
    cursor.execute("SELECT note FROM sluts_info WHERE id=?", (num,))
    note = cursor.fetchone()[0]
    return note


def get_origin(num):
    cursor.execute("SELECT origin FROM sluts_info WHERE id=?", (num,))
    origin = cursor.fetchone()[0]
    return origin


def get_votes(num):
    cursor.execute("SELECT votes FROM sluts_info WHERE id=?", (num,))
    votes: Dict = json.loads(cursor.fetchone()[0])
    return votes


def get_photo_id_by_id(id):
    cursor.execute("SELECT file_id FROM sluts_info WHERE id=?", (id,))
    photo_id = cursor.fetchone()[0]
    return photo_id


def max_photo_id_among_all(username):
    cursor.execute("SELECT MAX(id) FROM sluts_info WHERE origin!=?", (username,))
    photo_id = cursor.fetchone()[0]
    return photo_id


def max_photo_id_by_username(username):
    cursor.execute("SELECT MAX(id) FROM sluts_info WHERE origin=?", (username,))
    photo_id = cursor.fetchone()[0]
    return photo_id


def len_photos_by_username(username):
    cursor.execute("SELECT id FROM sluts_info WHERE origin=?", (username,))
    ln = cursor.fetchall()
    return len(ln)


def print_db():
    cursor.execute("SELECT * FROM sluts_info")
    rows = cursor.fetchall()
    for row in rows:
        print(row)


if __name__ == '__main__':
    get_last()
    print_db()
    # print(max_photo_id('nklnkk'))
    # print(len_photos_by_username('nklnkk'))
