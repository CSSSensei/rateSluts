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

    verified = True if result[0] else False
    if verified:
        return [True]
    cursor.execute("SELECT banned FROM users_info WHERE id=?", (id,))
    result = cursor.fetchone()
    if result[0]:
        return [False, -1]

    cursor.execute("SELECT attempts FROM users_info WHERE id=?", (id,))
    result = cursor.fetchone()[0]
    if result <= 0:
        cursor.execute("UPDATE users_info SET banned=?, attempts=? WHERE id=?", (True, 0, id,))
        conn.commit()
    # else:
    #     cursor.execute("UPDATE users_info SET attempts=? WHERE id=?", (result - 1, id,))
    #     conn.commit()
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


def delete_from_queue(id, num=0):
    if num==0:
        cursor.execute("UPDATE users_info SET queue=? WHERE id=?", (None, id,))
        conn.commit()
        return
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


def get_id_by_username(un):
    cursor.execute("SELECT id FROM users_info WHERE username=?", (un,))
    result = cursor.fetchone()
    if result is None:
        return None
    return result[0]


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
    cursor.execute("UPDATE users_info SET verified=?, banned=?, attempts=?, current=? WHERE id=?",
                   (True, False, 0, 0, id))
    conn.commit()


def get_users() -> set:
    cursor.execute("SELECT id FROM users_info WHERE verified = True")
    rows = cursor.fetchall()
    return set(row[0] for row in rows)


def add_girlphoto(id, num):
    cursor.execute("UPDATE users_info SET photos_ids=? WHERE id=?", (str(num), id,))
    conn.commit()


def get_not_incel() -> set:
    cursor.execute("SELECT id FROM users_info WHERE verified = False AND banned = False")
    rows = cursor.fetchall()
    return set(row[0] for row in rows)


def get_last_commit(id):
    cursor.execute("SELECT photos_ids FROM users_info WHERE id=?", (id,))
    rows = cursor.fetchone()[0]
    return int(rows)


def insert_last_rate(id, num):
    cursor.execute("UPDATE users_info SET attempts=? WHERE id=?", (num, id,))
    conn.commit()


def get_last_rate(id):
    cursor.execute("SELECT attempts FROM users_info WHERE id=?", (id,))
    rows = cursor.fetchone()[0]
    return rows


def add_current_state(id, num, username=0):
    if username == 0:
        cursor.execute("UPDATE users_info SET current=? WHERE id=?", (num, id,))
        return
    cursor.execute("UPDATE users_info SET current=?, username=? WHERE id=?", (num, username, id,))
    conn.commit()


def get_username_by_id(id):
    cursor.execute("SELECT username FROM users_info WHERE id=?", (id,))
    un = cursor.fetchone()[0]
    return str(un)


def get_ban(id):
    cursor.execute("UPDATE users_info SET banned=?, verified=? WHERE id=?", (True, False, id,))
    if cursor.rowcount == 0:
        return 0
    return 1


def get_current_state(id):
    cursor.execute("SELECT current FROM users_info WHERE id=?", (id,))
    state_photo: int = cursor.fetchone()[0]
    return state_photo


def delete_row(username):
    cursor.execute("DELETE FROM users_info WHERE username=?", (username,))
    conn.commit()
    if cursor.rowcount == 0:
        return 0
    return 1

def check_user(username):
    cursor.execute("SELECT id FROM users_info WHERE username=?", (username,))
    result = cursor.fetchone()
    if result is not None:
        return result[0]
    return None


def get_usersinfo_db():
    cursor.execute("SELECT * FROM users_info")
    rows = cursor.fetchall()
    return rows


def print_db():
    cursor.execute("SELECT * FROM users_info")
    rows = cursor.fetchall()
    for row in rows:
        print(row)


if __name__ == '__main__':
    print_db()
    print(get_last_commit(972753303))
