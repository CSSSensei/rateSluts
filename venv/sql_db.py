import datetime
import sqlite3
import json
from typing import Dict
import aiosqlite
from db_paths import db_paths

users_db = db_paths['users']
conn = sqlite3.connect(users_db)
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS users_info 
                  (id INTEGER PRIMARY KEY, username TEXT, banned BOOl, verified BOOL, attempts INTEGER, photos_ids TEXT, current INT, queue TEXT, new_user BOOL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS birthday 
                  (id INTEGER PRIMARY KEY, birthdate DATE)''')
cursor.close()
conn.close()


async def check_id(id: int, username: str) -> bool:
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT verified FROM users_info WHERE id=?", (id,))
        user_is_verified = await cursor.fetchone()

        if user_is_verified is None:
            await db.execute("INSERT INTO users_info (id, username, verified, banned, attempts, new_user) VALUES (?, ?, ?, ?, ?, ?)",
                                 (id, username, False, False, 5, True))
            await db.commit()
            return [False, 10]

        verified = True if user_is_verified[0] else False
        await db.execute("UPDATE users_info SET username=? WHERE id=?", (username, id))
        await db.commit()
        if verified:
            return [True]
        cursor = await db.execute("SELECT banned FROM users_info WHERE id=?", (id,))
        user_is_banned = await cursor.fetchone()
        if user_is_banned[0]:
            return [False, -1]
        return [False, 1]


async def check_new_user(id):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT new_user FROM users_info WHERE id=?", (id,))
        user_is_new = await cursor.fetchone()
        if user_is_new is None:
            db.execute("INSERT INTO users_info (id, new_user) VALUES (?, ?)", (id, False))
            await db.commit()
            return True
        if user_is_new[0] or user_is_new[0] is None:
            await db.execute("UPDATE users_info SET new_user=? WHERE id=?", (False, id))
            await db.commit()
            return True
        return False


async def add_new_birthday(user_id, date: int):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT * FROM birthday WHERE id=?", (user_id,))
        user_is_new = await cursor.fetchone()
        if user_is_new is None:
            await db.execute("INSERT INTO birthday (id, birthdate) VALUES (?, ?)", (user_id, date))
        else:
            await db.execute("UPDATE birthday SET birthdate=? WHERE id=?", (date, user_id))
        await db.commit()


async def get_birthday(user_id):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT birthdate FROM birthday WHERE id=?", (user_id,))
        date = await cursor.fetchone()
        if date:
            return date[0]
        return None

async def get_top_incels():
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT id FROM users_info WHERE verified = True")
        rows = await cursor.fetchall()
        return set(row[0] for row in rows) - {955289704}


async def add_to_queue(id, num):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT queue FROM users_info WHERE id=?", (id,))
        queue = await cursor.fetchone()
        if queue is None or queue[0] is None or queue[0] == '':
            queue = str(num)
        else:
            queue = set(map(int, queue[0].split(',')))
            queue.add(num)
            queue = ', '.join(map(str, queue))
        await db.execute("UPDATE users_info SET queue=? WHERE id=?", (queue, id,))
        await db.commit()


async def delete_from_queue(id, num=0):
    async with aiosqlite.connect(users_db) as db:
        if num==0:
            await db.execute("UPDATE users_info SET queue=? WHERE id=?", (None, id,))
            await db.commit()
            return
        cursor = await db.execute("SELECT queue FROM users_info WHERE id=?", (id,))
        queue = await cursor.fetchone()
        if queue is None or queue[0] is None or queue[0] == '':
            return
        else:
            queue = set(map(int, queue[0].split(',')))
            if num in queue:
                queue.remove(num)
                if len(queue) == 0:
                    queue = None
                    await db.execute("UPDATE users_info SET queue=? WHERE id=?", (queue, id,))
                    await db.commit()
                    return
            queue = ', '.join(map(str, queue))
        await db.execute("UPDATE users_info SET queue=? WHERE id=?", (queue, id,))
        await db.commit()


async def change_queue(id, queue):
    async with aiosqlite.connect(users_db) as db:
        await db.execute("UPDATE users_info SET queue=? WHERE id=?", (queue, id,))
        await db.commit()


async def get_id_by_username(un):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT id FROM users_info WHERE username=?", (un,))
        user_id = await cursor.fetchone()
        if user_id is None:
            return None
        return user_id[0]


async def get_queue(id):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT queue FROM users_info WHERE id=?", (id,))
        queue = await cursor.fetchone()
        if queue is None or queue[0] is None or queue[0] == '':
            return set()
        return set(map(int, queue[0].split(',')))


async def reduce_attempts(id: int):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT attempts FROM users_info WHERE id=?", (id,))
        attempts = (await cursor.fetchone())[0]
        await db.execute("UPDATE users_info SET attempts=? WHERE id=?", (attempts - 1, id,))
        await db.commit()
        return attempts


async def set_verified(id: int):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT * FROM users_info WHERE id=?", (id,))
        rows = await cursor.fetchall()
        if not rows:
            await db.execute("INSERT INTO users_info (id, verified, current, banned) VALUES (?, ?, ?, ?)",
                             (id, True, 0, False))
        else:
            await db.execute("UPDATE users_info SET verified=?, banned=?, current=? WHERE id=?",
                             (True, False, 0, id))
        await db.commit()


def sync_get_users():
    conn = sqlite3.connect(users_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users_info WHERE verified = True")
    rows = cursor.fetchall()
    return set(row[0] for row in rows)
    cursor.close()
    conn.close()


async def get_users():
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT id FROM users_info WHERE verified = True")
        rows = await cursor.fetchall()
        return set(row[0] for row in rows)


async def add_girlphoto(id, num):
    async with aiosqlite.connect(users_db) as db:
        await db.execute("UPDATE users_info SET photos_ids=? WHERE id=?", (str(num), id,))
        await db.commit()


async def get_not_incel():
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT id FROM users_info WHERE verified = False AND banned = False")
        rows = await cursor.fetchall()
        return set(row[0] for row in rows)


async def get_last_commit(id):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT photos_ids FROM users_info WHERE id=?", (id,))
        rows = (await cursor.fetchone())[0]
        return int(rows)


async def insert_last_rate(id, num):
    async with aiosqlite.connect(users_db) as db:
        await db.execute("UPDATE users_info SET attempts=? WHERE id=?", (num, id,))
        await db.commit()


async def get_last_rate(id):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT attempts FROM users_info WHERE id=?", (id,))
        rows = (await cursor.fetchone())[0]
        return rows


async def add_current_state(id, num, username=0):
    async with aiosqlite.connect(users_db) as db:
        if username == 0:
            await db.execute("UPDATE users_info SET current=? WHERE id=?", (num, id,))
            await db.commit()
            return
        await db.execute("UPDATE users_info SET current=?, username=? WHERE id=?", (num, username, id,))
        await db.commit()


async def get_username_by_id(id):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT username FROM users_info WHERE id=?", (id,))
        un = (await cursor.fetchone())[0]
        return str(un)


async def get_ban(id):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT username FROM users_info WHERE id=?", (id,))
        user_id = await cursor.fetchone()
        if user_id is not None:
            await db.execute("UPDATE users_info SET banned=?, verified=? WHERE id=?", (True, False, id,))
            await db.commit()
            return 1
        return 0


async def get_unban(id):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT username FROM users_info WHERE id=?", (id,))
        user_id = await cursor.fetchone()
        if user_id is not None:
            await db.execute("UPDATE users_info SET banned=?, verified=? WHERE id=?", (False, False, id,))
            await db.commit()
            return 1
        return 0


async def get_current_state(id):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT current FROM users_info WHERE id=?", (id,))
        state_photo = (await cursor.fetchone())[0]
        return state_photo


async def delete_row(username):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.cursor()
        await cursor.execute("DELETE FROM users_info WHERE username=?", (username,))

        await db.commit()

        if cursor.rowcount == 0:
            return 0
        return 1


async def check_user(username):
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT id FROM users_info WHERE username=?", (username,))
        user_id = await cursor.fetchone()
        if user_id is not None:
            return user_id[0]
        return None


async def get_usersinfo_db():
    async with aiosqlite.connect(users_db) as db:
        cursor = await db.execute("SELECT * FROM users_info")
        rows = await cursor.fetchall()
        return rows


def print_db():
    conn = sqlite3.connect(users_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users_info")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()


if __name__ == '__main__':
    print_db()
    print(sync_get_users())