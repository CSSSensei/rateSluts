import datetime
import sqlite3
import json
from typing import Dict
import aiosqlite
from db_paths import db_paths

db = db_paths['users']
conn = sqlite3.connect(db)
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS users_info 
                  (id INTEGER PRIMARY KEY, username TEXT, banned BOOl, verified BOOL, attempts INTEGER, photos_ids TEXT, current INT, queue TEXT, new_user BOOL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS birthday 
                  (id INTEGER PRIMARY KEY, birthdate DATE)''')
conn.close()


async def get_async_connection():
    async_connection = await aiosqlite.connect(db)
    return async_connection


async def check_id(id: int, username: str) -> bool:
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT verified FROM users_info WHERE id=?", (id,))
        user_is_verified = await cursor.fetchone()

        if user_is_verified is None:
            await cursor.execute("INSERT INTO users_info (id, username, verified, banned, attempts, new_user) VALUES (?, ?, ?, ?, ?, ?)",
                           (id, username, False, False, 5, True))
            await async_connection.commit()
            return [False, 10]

        verified = True if user_is_verified[0] else False
        if verified:
            return [True]
        await cursor.execute("SELECT banned FROM users_info WHERE id=?", (id,))
        user_is_banned = await cursor.fetchone()
        if user_is_banned[0]:
            return [False, -1]
        return [False, 1]


async def check_new_user(id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT new_user FROM users_info WHERE id=?", (id,))
        user_is_new = await cursor.fetchone()
        if user_is_new is None:
            await cursor.execute("INSERT INTO users_info (id, new_user) VALUES (?, ?)", (id, False))
            await async_connection.commit()
            return True
        if user_is_new[0] or user_is_new[0] is None:
            await cursor.execute("UPDATE users_info SET new_user=? WHERE id=?", (False, id))
            await async_connection.commit()
            return True
        return False


async def add_new_birthday(user_id, date: int):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await ursor.execute("SELECT * FROM birthday WHERE id=?", (user_id,))
        user_is_new = await cursor.fetchone()
        if user_is_new is None:
            await cursor.execute("INSERT INTO birthday (id, birthdate) VALUES (?, ?)", (user_id, date))
        else:
            await cursor.execute("UPDATE birthday SET birthdate=? WHERE id=?", (date, user_id))
        await async_connection.commit()


async def get_birthday(user_id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT birthdate FROM birthday WHERE id=?", (user_id,))
        date = await cursor.fetchone()
        if date:
            return date[0]
        return None

async def get_top_incels():
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT id FROM users_info WHERE verified = True")
        rows = await cursor.fetchall()
        return set(row[0] for row in rows) - {955289704}


async def add_to_queue(id, num):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT queue FROM users_info WHERE id=?", (id,))
        queue = await cursor.fetchone()
        if queue is None or queue[0] is None or queue[0] == '':
            queue = str(num)
        else:
            queue = set(map(int, queue[0].split(',')))
            queue.add(num)
            queue = ', '.join(map(str, queue))
        await cursor.execute("UPDATE users_info SET queue=? WHERE id=?", (queue, id,))
        await async_connection.commit()


async def delete_from_queue(id, num=0):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        if num==0:
            await cursor.execute("UPDATE users_info SET queue=? WHERE id=?", (None, id,))
            await async_connection.commit()
            return
        await cursor.execute("SELECT queue FROM users_info WHERE id=?", (id,))
        queue = await cursor.fetchone()
        if queue is None or queue[0] is None or queue[0] == '':
            return
        else:
            queue = set(map(int, queue[0].split(',')))
            if num in queue:
                queue.remove(num)
                if len(queue) == 0:
                    queue = None
                    await cursor.execute("UPDATE users_info SET queue=? WHERE id=?", (queue, id,))
                    await async_connection.commit()
                    return
            queue = ', '.join(map(str, queue))
        await cursor.execute("UPDATE users_info SET queue=? WHERE id=?", (queue, id,))
        await async_connection.commit()


async def change_queue(id, queue):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("UPDATE users_info SET queue=? WHERE id=?", (queue, id,))
        await async_connection.commit()


async def get_id_by_username(un):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT id FROM users_info WHERE username=?", (un,))
        user_id = await cursor.fetchone()
        if user_id is None:
            return None
        return user_id[0]


async def get_queue(id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT queue FROM users_info WHERE id=?", (id,))
        queue = await cursor.fetchone()
        if queue is None or queue[0] is None or queue[0] == '':
            return set()
        return set(map(int, queue[0].split(',')))


async def reduce_attempts(id: int):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT attempts FROM users_info WHERE id=?", (id,))
        attempts = (await cursor.fetchone())[0]
        await cursor.execute("UPDATE users_info SET attempts=? WHERE id=?", (attempts - 1, id,))
        await async_connection.commit()
        return attempts


async def set_verified(id: int):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM users_info WHERE id=?", (id,))
        rows = await cursor.fetchall()
        if not rows:
            await cursor.execute("INSERT INTO users_info (id, verified, current, banned) VALUES (?, ?, ?, ?)",
                           (id, True, 0, False))
        else:
            await cursor.execute("UPDATE users_info SET verified=?, banned=?, current=? WHERE id=?",
                           (True, False, 0, id))
        await async_connection.commit()


def sync_get_users():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users_info WHERE verified = True")
    rows = cursor.fetchall()
    return set(row[0] for row in rows)
    conn.close()


async def get_users():
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT id FROM users_info WHERE verified = True")
        rows = await cursor.fetchall()
        return set(row[0] for row in rows)


async def add_girlphoto(id, num):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("UPDATE users_info SET photos_ids=? WHERE id=?", (str(num), id,))
        await async_connection.commit()


async def get_not_incel():
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT id FROM users_info WHERE verified = False AND banned = False")
        rows = await cursor.fetchall()
        return set(row[0] for row in rows)


async def get_last_commit(id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT photos_ids FROM users_info WHERE id=?", (id,))
        rows = (await cursor.fetchone())[0]
        return int(rows)


async def insert_last_rate(id, num):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("UPDATE users_info SET attempts=? WHERE id=?", (num, id,))
        await async_connection.commit()


async def get_last_rate(id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT attempts FROM users_info WHERE id=?", (id,))
        rows = (await cursor.fetchone())[0]
        return rows


async def add_current_state(id, num, username=0):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        if username == 0:
            await cursor.execute("UPDATE users_info SET current=? WHERE id=?", (num, id,))
            await async_connection.commit()
            return
        await cursor.execute("UPDATE users_info SET current=?, username=? WHERE id=?", (num, username, id,))
        await async_connection.commit()


async def get_username_by_id(id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT username FROM users_info WHERE id=?", (id,))
        un = (await cursor.fetchone())[0]
        return str(un)


async def get_ban(id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT username FROM users_info WHERE id=?", (id,))
        user_id = await cursor.fetchone()
        if user_id is not None:
            await cursor.execute("UPDATE users_info SET banned=?, verified=? WHERE id=?", (True, False, id,))
            await async_connection.commit()
            return 1
        return 0


async def get_unban(id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT username FROM users_info WHERE id=?", (id,))
        user_id = await cursor.fetchone()
        if user_id is not None:
            await cursor.execute("UPDATE users_info SET banned=?, verified=? WHERE id=?", (False, False, id,))
            await async_connection.commit()
            return 1
        return 0



async def get_current_state(id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT current FROM users_info WHERE id=?", (id,))
        state_photo = (await cursor.fetchone())[0]
        return state_photo


async def delete_row(username):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("DELETE FROM users_info WHERE username=?", (username,))
        await async_connection.commit()
        if cursor.rowcount == 0:
            return 0
        return 1


async def check_user(username):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT id FROM users_info WHERE username=?", (username,))
        user_id = await cursor.fetchone()
        if user_id is not None:
            return user_id[0]
        return None


async def get_usersinfo_db():
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM users_info")
        rows = await cursor.fetchall()
        return rows


def print_db():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users_info")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()


if __name__ == '__main__':
    print_db()
    print(get_users())