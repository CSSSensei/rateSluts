import datetime
import sqlite3
import json
from typing import Dict


conn = sqlite3.connect('usersDB.db')
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS users_info 
                  (id INTEGER PRIMARY KEY, username TEXT, banned BOOl, verified BOOL, attempts INTEGER, photos_ids TEXT, current INT, queue TEXT, new_user BOOL)''')



def check_id(id: int, username: str) -> bool:
    cursor.execute("SELECT verified FROM users_info WHERE id=?", (id,))
    user_is_verified = cursor.fetchone()

    if user_is_verified is None:
        cursor.execute("INSERT INTO users_info (id, username, verified, banned, attempts, new_user) VALUES (?, ?, ?, ?, ?, ?)",
                       (id, username, False, False, 5, True))
        conn.commit()
        return [False, 10]

    verified = True if user_is_verified[0] else False
    if verified:
        return [True]
    cursor.execute("SELECT banned FROM users_info WHERE id=?", (id,))
    user_is_banned = cursor.fetchone()
    if user_is_banned[0]:
        return [False, -1]
    return [False, 1]


def check_new_user(id):
    cursor.execute("SELECT new_user FROM users_info WHERE id=?", (id,))
    user_is_new = cursor.fetchone()
    if user_is_new is None:
        cursor.execute("INSERT INTO users_info (id, new_user) VALUES (?, ?)", (id, False))
        conn.commit()
        return True
    if user_is_new[0] or user_is_new[0] is None:
        cursor.execute("UPDATE users_info SET new_user=? WHERE id=?", (False, id))
        conn.commit()
        return True
    return False


def add_to_queue(id, num):
    cursor.execute("SELECT queue FROM users_info WHERE id=?", (id,))
    queue = cursor.fetchone()[0]
    if queue is None or queue == '':
        queue = str(num)
    else:
        queue = set(map(int, queue.split(',')))
        queue.add(num)
        queue = ', '.join(map(str, queue))
    cursor.execute("UPDATE users_info SET queue=? WHERE id=?", (queue, id,))
    conn.commit()


def delete_from_queue(id, num=0):
    if num==0:
        cursor.execute("UPDATE users_info SET queue=? WHERE id=?", (None, id,))
        conn.commit()
        return
    cursor.execute("SELECT queue FROM users_info WHERE id=?", (id,))
    queue = cursor.fetchone()[0]
    if queue is None or queue == '':
        return
    else:
        queue = set(map(int, queue.split(',')))
        if num in queue:
            queue.remove(num)
            if len(queue) == 0:
                queue = None
                cursor.execute("UPDATE users_info SET queue=? WHERE id=?", (queue, id,))
                conn.commit()
                return
        queue = ', '.join(map(str, queue))
    cursor.execute("UPDATE users_info SET queue=? WHERE id=?", (queue, id,))
    conn.commit()


def change_queue(id, queue):
    cursor.execute("UPDATE users_info SET queue=? WHERE id=?", (queue, id,))
    conn.commit()


def get_id_by_username(un):
    cursor.execute("SELECT id FROM users_info WHERE username=?", (un,))
    user_id = cursor.fetchone()
    if user_id is None:
        return None
    return user_id[0]


def get_queue(id):
    cursor.execute("SELECT queue FROM users_info WHERE id=?", (id,))
    queue = cursor.fetchone()[0]
    if queue is None or queue == '':
        return set()
    return set(map(int, queue.split(',')))


def reduce_attempts(id: int):
    cursor.execute("SELECT attempts FROM users_info WHERE id=?", (id,))
    attempts = cursor.fetchone()[0]
    cursor.execute("UPDATE users_info SET attempts=? WHERE id=?", (attempts - 1, id,))
    conn.commit()
    return attempts


def set_verified(id: int):
    cursor.execute("SELECT * FROM users_info WHERE id=?", (id,))
    rows = cursor.fetchall()
    if not rows:
        cursor.execute("INSERT INTO users_info (id, verified, current, banned) VALUES (?, ?, ?, ?)",
                       (id, True, 0, False))
        conn.commit()
    else:
        cursor.execute("UPDATE users_info SET verified=?, banned=?, current=? WHERE id=?",
                       (True, False, 0, id))
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
    cursor.execute("SELECT username FROM users_info WHERE id=?", (id,))
    user_id = cursor.fetchone()
    if user_id is not None:
        cursor.execute("UPDATE users_info SET banned=?, verified=? WHERE id=?", (True, False, id,))
        conn.commit()
        return 1
    return 0


def get_unban(id):
    cursor.execute("SELECT username FROM users_info WHERE id=?", (id,))
    user_id = cursor.fetchone()
    if user_id is not None:
        cursor.execute("UPDATE users_info SET banned=?, verified=? WHERE id=?", (False, False, id,))
        conn.commit()
        return 1
    return 0



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
    user_id = cursor.fetchone()
    if user_id is not None:
        return user_id[0]
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
    print(get_users())