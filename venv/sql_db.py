import datetime
import sqlite3
import json
from typing import Dict

# Creating a database connection
conn = sqlite3.connect('usersDB.db')
cursor = conn.cursor()

# Creating a table with id and info columns
cursor.execute('''CREATE TABLE IF NOT EXISTS users_info 
                  (id INTEGER PRIMARY KEY, username TEXT, banned BOOl, verified BOOL, attempts INTEGER, photos_ids TEXT, current INT, queue TEXT)''')


# Function to check if id exists in the database
def check_id(id: int, username: str) -> bool:
    # Checking if id exists
    cursor.execute("SELECT verified FROM users_info WHERE id=?", (id,))
    result = cursor.fetchone()

    if result is None:
        cursor.execute("INSERT INTO users_info (id, username, verified, banned, attempts) VALUES (?, ?, ?, ?, ?)",
                       (id, username, False, False, 5))
        conn.commit()
        return [False, 5]
    if result[0]:
        return [True]
    cursor.execute("SELECT attempts FROM users_info WHERE id=?", (id,))
    result = cursor.fetchone()[0]
    if result <= 0:
        cursor.execute("UPDATE users_info SET banned=?, attempts=? WHERE id=?", (True, 0, id,))
        conn.commit()
    else:
        cursor.execute("UPDATE users_info SET attempts=? WHERE id=?", (result - 1, id,))
        conn.commit()
    return [False, result]


def add_to_queue(id, num):
    cursor.execute("SELECT queue FROM users_info WHERE id=?", (id,))
    result = cursor.fetchone()[0]
    if result is None or result == '':
        result = str(num)
    else:
        result = set(map(int, result.split(',')))
        result.add(num)
        result = ', '.join(map(str, result))
    cursor.execute("UPDATE users_info SET queue=? WHERE id=?", (result, id,))
    conn.commit()


def delete_from_queue(id, num):
    cursor.execute("SELECT queue FROM users_info WHERE id=?", (id,))
    result = cursor.fetchone()[0]
    if result is None or result == '':
        return
    else:
        result = set(map(int, result.split(',')))
        if num in result:
            result.remove(num)
            if len(result) == 0:
                result = None
                cursor.execute("UPDATE users_info SET queue=? WHERE id=?", (result, id,))
                conn.commit()
                return
        result = ', '.join(map(str, result))
    cursor.execute("UPDATE users_info SET queue=? WHERE id=?", (result, id,))
    conn.commit()


def get_queue(id):
    cursor.execute("SELECT queue FROM users_info WHERE id=?", (id,))
    result = cursor.fetchone()[0]
    if result is None or result == '':
        return set()
    return set(map(int, result.split(',')))


def reduce_attempts(id: int):
    cursor.execute("SELECT attempts FROM users_info WHERE id=?", (id,))
    result = cursor.fetchone()[0]
    cursor.execute("UPDATE users_info SET attempts=? WHERE id=?", (result - 1, id,))
    conn.commit()
    return result


def set_verified(id: int()):
    cursor.execute("UPDATE users_info SET verified=?, banned=?, attempts=? WHERE id=?", (True, False, 5, id))
    conn.commit()


def get_users():
    cursor.execute("SELECT id FROM users_info WHERE verified = True")
    rows = cursor.fetchall()
    return set(row[0] for row in rows)


def add_girlphoto(id, num):
    cursor.execute("SELECT photos_ids FROM users_info WHERE id=?", (id,))
    rows = cursor.fetchone()[0]
    rows = '' if rows is None else rows + ', '
    cursor.execute("UPDATE users_info SET photos_ids=? WHERE id=?", (rows + str(num), id,))
    conn.commit()


def get_last_commit(id):
    cursor.execute("SELECT photos_ids FROM users_info WHERE id=?", (id,))
    rows = list(map(int, cursor.fetchone()[0].split(',')))
    return int(rows[-1])


def add_current_state(id, num, username=0):
    if username == 0:
        cursor.execute("UPDATE users_info SET current=? WHERE id=?", (num, id,))
        return
    cursor.execute("UPDATE users_info SET current=?, username=? WHERE id=?", (num, username, id,))
    conn.commit()


def get_current_state(id):
    cursor.execute("SELECT current FROM users_info WHERE id=?", (id,))
    state_photo: int = cursor.fetchone()[0]
    return state_photo


def print_db():
    cursor.execute("SELECT * FROM users_info")
    rows = cursor.fetchall()
    for row in rows:
        print(row)


if __name__ == '__main__':
    print_db()
