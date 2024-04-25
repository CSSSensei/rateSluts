import asyncio
import datetime
import sqlite3
import json
import time
from typing import Dict, Union
from parser import *
import aiosqlite
from db_paths import db_paths

db = db_paths['admin']
conn = sqlite3.connect(db)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS admins_info 
                  (id INTEGER PRIMARY KEY, active BOOL, trigger TEXT, day_of_week TEXT,
                  hour TEXT, minute TEXT, groups_to_moderate TEXT, mode INTEGER, extra2 TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS group_parser 
                  (id INTEGER PRIMARY KEY, group_domain TEXT , active BOOL, top_likes BOOL,
                  photo_amount INTEGER, time_delta TEXT, last_update INTEGER, name TEXT, cover TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS group_photos 
                  (id INTEGER PRIMARY KEY, group_name TEXT , caption TEXT, url TEXT)''')

cursor.execute("SELECT id FROM admins_info WHERE active=True")
admins = cursor.fetchall()
if not admins:
    cursor.execute("SELECT * FROM admins_info WHERE id=972753303")
    admins = cursor.fetchone()
    if admins is None:
        cursor.execute("INSERT INTO admins_info (id, active, trigger, day_of_week, hour, minute, mode) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (972753303, True, '-1', '1, 2, 3, 4, 5, 6, 7', '20', '00', 2))
        conn.commit()
    else:
        cursor.execute("UPDATE admins_info SET active=True WHERE id=972753303")
        conn.commit()
conn.close()


async def get_admins():
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT id FROM admins_info WHERE active=True")
        rows = await cursor.fetchall()
        return set(row[0] for row in rows)


async def get_message_to_delete(user_id):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT trigger FROM admins_info WHERE id=?", (user_id,))
        rows = (await cursor.fetchone())[0]
        if rows == '-1':
            return None
        return rows


async def set_message_to_delete(user_id, message_id: str):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("UPDATE admins_info SET trigger=? WHERE id=?", (message_id, user_id,))
        await async_connection.commit()


async def set_admin(user_id):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM admins_info WHERE id=?", (user_id,))
        rows = await cursor.fetchall()
        if not rows:
            await cursor.execute("INSERT INTO admins_info (id, active, trigger, day_of_week, hour, minute, mode) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, True, '-1', '1, 2, 3, 4, 5, 6, 7', '20', '00', 1))
            await async_connection.commit()

        else:
            await cursor.execute("UPDATE admins_info SET active=? WHERE id=?", (True, user_id,))
            await async_connection.commit()


async def update_groupnames():
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT id FROM group_parser")
        rows = await cursor.fetchall()
        for row in rows:
            id = row[0]
            await cursor.execute("SELECT group_domain FROM group_parser WHERE id=?", (id,))
            domain = (await cursor.fetchone())[0]
            name, photo = api_group_name(domain)
            await asyncio.sleep(0.4)
            await cursor.execute("UPDATE group_parser SET name=?, cover=? WHERE group_domain=?", (name, photo, domain,))
            await async_connection.commit()


async def add_to_queue_group_photo(user_id: int, num: str):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT extra2 FROM admins_info WHERE id=?", (user_id,))
        queue = await cursor.fetchone()
        if queue is None or queue[0] == '' or queue[0] is None:
            queue = num
        else:
            queue = set(queue[0].split(', '))
            queue.add(num)
            queue = ', '.join(queue)
        await cursor.execute("UPDATE admins_info SET extra2=? WHERE id=?", (queue, user_id,))
        await async_connection.commit()


async def get_admins_queue(user_id: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT extra2 FROM admins_info WHERE id=?", (user_id,))
        queue = await cursor.fetchone()
        if queue is None or queue[0] == '' or queue[0] is None:
            return set()
        return set(queue[0].split(', '))


async def remove_from_admins_queue(user_id, num):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        if num==0:
            await cursor.execute("UPDATE admins_info SET extra2=? WHERE id=?", (None, user_id,))
            await async_connection.commit()
            return
        await cursor.execute("SELECT extra2 FROM admins_info WHERE id=?", (user_id,))
        queue = await cursor.fetchone()
        if queue is None or queue[0] == '' or queue[0] is None:
            return
        else:
            queue = set(queue[0].split(', '))
            if num in queue:
                queue.remove(num)
                if len(queue) == 0:
                    queue = None
                    await cursor.execute("UPDATE admins_info SET extra2=? WHERE id=?", (queue, user_id,))
                    await async_connection.commit()
                    return
            queue = ', '.join(map(str, queue))
        await cursor.execute("UPDATE admins_info SET extra2=? WHERE id=?", (queue, user_id,))
        await async_connection.commit()


async def set_admin_mode(user_id, mode):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM admins_info WHERE id=?", (user_id,))
        rows = await cursor.fetchall()
        if not rows:
            await cursor.execute("INSERT INTO admins_info (id, active, mode) VALUES (?, ?, ?)",
                           (user_id, True, mode))
            await async_connection.commit()
        else:
            await cursor.execute("UPDATE admins_info SET mode=? WHERE id=?", (mode, user_id,))
            await async_connection.commit()


async def set_inactive(user_id: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM admins_info WHERE id=?", (user_id,))
        rows = await cursor.fetchall()
        if not rows:
            await cursor.execute(
                "INSERT INTO admins_info (id, active, trigger, day_of_week, hour, minute, mode) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, False, '-1', '1, 2, 3, 4, 5, 6, 7', '20', '00', 1))
            await async_connection.commit()

        else:
            await cursor.execute("UPDATE admins_info SET active=? WHERE id=?", (False, user_id,))
            await async_connection.commit()


async def get_settings(user_id: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM admins_info WHERE id=?", (user_id,))
        rows = await cursor.fetchone()
        return rows


async def get_weekdays(user_id: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT day_of_week FROM admins_info WHERE id=?", (user_id,))
        rows = await cursor.fetchone()
        if rows is None or rows[0] is None:
            return set()
        weekdays = set(map(int, rows[0].split(',')))
        return weekdays


async def change_weekdays(user_id: int, day: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT day_of_week FROM admins_info WHERE id=?", (user_id,))
        rows = await cursor.fetchone()
        if rows is None or rows[0] is None:
            weekdays = str(day)
        else:
            rows = set(map(int, rows[0].split(',')))
            if day in rows:
                rows.remove(day)
            else:
                rows.add(day)
            if len(rows) == 0:
                weekdays = None
            else:
                weekdays = ', '.join(map(str, rows))
        if weekdays is None:
            await cursor.execute("UPDATE admins_info SET day_of_week=NULL WHERE id=?", (user_id,))
        else:
            await cursor.execute("UPDATE admins_info SET day_of_week=? WHERE id=?", (weekdays, user_id,))
        await async_connection.commit()


async def get_group_domain(group_id: Union[str, int]):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT group_domain FROM group_parser WHERE id=?", (group_id,))
        domain = await cursor.fetchone()
        return domain[0] if domain is not None else None


async def get_async_admin_connection():
    async_connection = await aiosqlite.connect(db)
    return async_connection


async def get_group_sets(group_id: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM group_parser WHERE id=?", (group_id,))
        rows = await cursor.fetchone()
        if rows[7] is None:
            name, photo = await api_group_name(rows[1])  # Assuming api_group_name is an asynchronous function
            await cursor.execute("UPDATE group_parser SET name=?, cover=? WHERE id=?", (name, photo, group_id))
            await async_connection.commit()
            return rows[:7] + (name, photo)
        return rows

async def send_photos_by_id(num: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM group_photos WHERE id=?", (num,))
        rows = await cursor.fetchone()
        return rows


async def get_group_name(domain: Union[str, int]):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        if isinstance(domain, str):
            await cursor.execute("SELECT name FROM group_parser WHERE group_domain=?", (domain,))
            rows = await cursor.fetchone()
            if rows is None:
                return None
            else:
                if rows[0] is None:
                    name, photo = api_group_name(domain)
                    await cursor.execute("UPDATE group_parser SET name=?, cover=? WHERE group_domain=?", (name, photo, domain,))
                    await async_connection.commit()
                    return name.replace('<','').replace('>','')
                return rows[0].replace('<','').replace('>','')
        else:
            await cursor.execute("SELECT name FROM group_parser WHERE id=?", (domain,))
            rows = await cursor.fetchone()
            if rows is None:
                return None
            else:
                if rows[0] is None:
                    name, photo = api_group_name(domain)
                    await cursor.execute("UPDATE group_parser SET name=?, cover=? WHERE group_domain=?", (name, photo, domain,))
                    await async_connection.commit()
                    return name.replace('<','').replace('>','')
                return rows[0].replace('<','').replace('>','')



async def get_active_groups():
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT id FROM group_parser WHERE active=?", (True,))
        rows = await cursor.fetchall()
        return set(i[0] for i in rows) if rows is not None else None


async def get_last_group():
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT MAX(id) FROM group_parser")
        rows = await cursor.fetchone()
        if rows is None:
            return 0
        return rows[0] if rows[0] is not None else 0


async def switch_active(group_id: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT active FROM group_parser WHERE id=?", (group_id,))
        active = (await cursor.fetchone())[0]
        await cursor.execute("UPDATE group_parser SET active=? WHERE id=?", (not active, group_id,))
        await async_connection.commit()


async def switch_top_likes(group_id: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT top_likes FROM group_parser WHERE id=?", (group_id,))
        top_likes = (await cursor.fetchone())[0]
        await cursor.execute("UPDATE group_parser SET top_likes=? WHERE id=?", (not top_likes, group_id,))
        await async_connection.commit()


async def change_amount(group_id: int, photo_amount: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("UPDATE group_parser SET photo_amount=? WHERE id=?", (photo_amount, group_id,))
        await async_connection.commit()


async def change_date(group_id: int, date: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("UPDATE group_parser SET time_delta=? WHERE id=?", (date, group_id,))
        await async_connection.commit()


async def change_hour(user_id: int, hour: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("UPDATE admins_info SET hour=? WHERE id=?", (str(hour), user_id,))
        await async_connection.commit()


async def change_minute(user_id: int, minute: str):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("UPDATE admins_info SET minute=? WHERE id=?", (minute, user_id,))
        await async_connection.commit()


async def add_group(user_id: int, domain: str):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT groups_to_moderate FROM admins_info WHERE id=?", (user_id,))
        groups = (await cursor.fetchone())[0]
        num = await get_last_group() + 1
        if groups is None or groups == '':
            groups = str(num)
        else:
            groups = set(map(int, groups.split(',')))
            for id in groups:
                if domain == await get_group_domain(id):
                    return -1, id
            groups.add(num)
            groups = ', '.join(map(str, groups))
        await cursor.execute("UPDATE admins_info SET groups_to_moderate=? WHERE id=?", (groups, user_id,))
        await async_connection.commit()
        name, photo = api_group_name(domain)
        await cursor.execute("INSERT INTO group_parser (id, group_domain, active, top_likes, photo_amount, time_delta, last_update, name, cover) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (num, domain, True, True, 6, 0, 0, name, photo))
        await async_connection.commit()
        return num, num


async def update_time(group_id: int, time_now=None):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        if time_now is None:
            time_now = int(time.time())
        await cursor.execute("UPDATE group_parser SET last_update=? WHERE id=?", (time_now, group_id))
        await async_connection.commit()  # Change conn to async_connection


async def delete_group(group_id: int, user_id: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute('DELETE FROM group_parser WHERE id=?', (group_id,))
        await async_connection.commit()
        await cursor.execute("SELECT groups_to_moderate FROM admins_info WHERE id=?", (user_id,))
        groups = set(map(int, cursor.fetchone()[0].split(',')))
        groups.remove(group_id)
        if len(groups) == 0:
            groups = None
        else:
            groups = ', '.join(map(str, groups))
        await cursor.execute("UPDATE admins_info SET groups_to_moderate=? WHERE id=?", (groups, user_id,))
        await async_connection.commit()


async def last_group_photo_id():
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT MAX(id) FROM group_photos")
        rows = (await cursor.fetchone())[0]
        if rows is None:
            return 0
        return rows


async def add_group_photo(num, origin, caption, url):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("INSERT INTO group_photos (id, group_name, caption, url) VALUES (?, ?, ?, ?)",
                       (num, origin, caption, url))
        await async_connection.commit()


async def get_group_photo_info(num):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM group_photos WHERE id=?", (num,))
        rows = await cursor.fetchone()
        return rows


async def del_group_photo(num):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute('DELETE FROM group_photos WHERE id=?', (num,))
        await async_connection.commit()


async def get_hour(user_id: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT hour FROM admins_info WHERE id=?", (user_id,))
        rows = await cursor.fetchone()
        return int(rows[0])


async def set_hour(user_id: int, hour: str):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("UPDATE admins_info SET hour=? WHERE id=?", (hour, user_id,))
        await async_connection.commit()


async def get_minute(user_id: int):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT minute FROM admins_info WHERE id=?", (user_id,))
        rows = await cursor.fetchone()
        return int(rows[0])


async def set_minute(user_id: int, minute: str):
    async_connection = await get_async_admin_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("UPDATE admins_info SET minute=? WHERE id=?", (minute, user_id,))
        await async_connection.commit()


def check_minutes(minute: str):
    try:
        number = int(minute)
        if 0 <= number <= 59:
            return True
        else:
            return False
    except ValueError:
        return False


def check_hours(hour: str):
    try:
        number = int(hour)
        if 0 <= number <= 23:
            return True
        else:
            return False
    except ValueError:
        return False


if __name__ == '__main__':

    cursor.execute("SELECT * FROM admins_info")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    cursor.execute("SELECT * FROM group_parser")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    print()

    # cursor.execute("SELECT * FROM group_photos")
    # rows = cursor.fetchall()
    # for row in rows:
    #     print(row)
    #
    # send_photos_by_id(44)
