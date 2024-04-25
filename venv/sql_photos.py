import datetime
import sqlite3
import json
from typing import Dict
from sql_db import get_username_by_id
import aiosqlite
from db_paths import db_paths

db = db_paths['sluts']
conn = sqlite3.connect(db)
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS sluts_info 
                  (id INT PRIMARY KEY, note TEXT, votes TEXT, file_id TEXT, origin TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS average 
                  (id INT PRIMARY KEY, sum INT, amount INT, overshoot INT, hit INT, hit_amount INT, afk_times INT, last_upd INT, total_time INT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS results
                  (id INT PRIMARY KEY, photo TEXT, rate FLOAT, user_id INT)''')
conn.close()

async def add_not_incel_photo(num, photo, user_id, rate=-1):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("INSERT INTO results (id, photo, rate, user_id) VALUES (?, ?, ?, ?)", (num, photo, rate, user_id))
        await async_connection.commit()


async def add_new_user_to_average(user_id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute(
            "INSERT INTO average (id, sum, amount, overshoot, hit, hit_amount, afk_times, last_upd, total_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, 0, 0, 0, 0, 0, 0, 0, 0))
        await async_connection.commit()


async def get_last_upd(user_id: int):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT last_upd FROM average WHERE id=?", (user_id,))
        last_upd = await cursor.fetchone()
        if last_upd is None:
            await add_new_user_to_average(user_id)
            return 0
        return last_upd[0]


async def increment_time(user_id: int, time_delta: int, current_time: int):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT total_time FROM average WHERE id=?", (user_id,))
        total_time = await cursor.fetchone()
        if total_time is None:
            await add_new_user_to_average(user_id)
            total_time = 0
        else:
            total_time = total_time[0]
        await cursor.execute("UPDATE average SET total_time=?, last_upd=? WHERE id=?", (total_time + time_delta, current_time, user_id))
        await async_connection.commit()


async def change_last_update(user_id: int, current_time: int):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("UPDATE average SET last_upd=? WHERE id=?", (current_time, user_id))
        await async_connection.commit()


def convert_unix_time(unix_time):
    days, remainder = divmod(unix_time, 24 * 3600)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    time_units = []

    if days > 0:
        time_units.append(f"{days} дн.")
    if hours > 0 or days > 0:
        time_units.append(f"{hours} ч.")
    if minutes > 0 or hours > 0 or days > 0:
        time_units.append(f"{minutes} мин.")
    time_units.append(f"{seconds} с.")

    return ' '.join(time_units)


async def get_not_incel_rate(num):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT rate FROM results WHERE id=?", (num,))
        rate = await cursor.fetchone()
        return None if rate is None else rate[0]


async def add_overshoot(user_id: int):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT overshoot FROM average WHERE id=?", (user_id,))
        rows = await cursor.fetchone()
        if rows is None:
            await add_new_user_to_average(user_id)
            rows = 0
        else:
            rows = rows[0]
        await cursor.execute("UPDATE average SET overshoot=? WHERE id=?", (rows + 1, user_id))
        await async_connection.commit()


async def add_hit(user_id: int, hit: int = 0):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT hit_amount FROM average WHERE id=?", (user_id,))
        rows = await cursor.fetchone()
        if rows is None:
            await add_new_user_to_average(user_id)
            rows = 0
        else:
            rows = rows[0]
        await cursor.execute("UPDATE average SET hit_amount=? WHERE id=?", (rows + 1, user_id))
        await async_connection.commit()
        if hit != 0:
            await cursor.execute("SELECT hit FROM average WHERE id=?", (user_id,))
            hit_num = (await cursor.fetchone())[0]
            await cursor.execute("UPDATE average SET hit=? WHERE id=?", (hit_num + 1, user_id))
            await async_connection.commit()


async def add_afk(user_id: int):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT afk_times FROM average WHERE id=?", (user_id,))
        rows = await cursor.fetchone()
        if rows is None:
            await add_new_user_to_average(user_id)
            rows = 0
        else:
            rows = rows[0]
        await cursor.execute("UPDATE average SET afk_times=? WHERE id=?", (rows + 1, user_id))
        await async_connection.commit()


async def add_rate_not_incel(num, rate):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("UPDATE results SET rate=? WHERE id=?", (rate, num))
        await async_connection.commit()


async def get_avgs_not_incel(user_id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT rate FROM results WHERE user_id=?", (user_id,))
        rate = await cursor.fetchall()
        return rate


async def add_rate_to_avg(user_id: int, rate: int):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT sum, amount FROM average WHERE id=?", (user_id,))
        rate_rows = await cursor.fetchone()
        if rate_rows is None:
            await cursor.execute("INSERT INTO average (id, sum, amount) VALUES (?, ?, ?)",
                           (user_id, rate, 1))
        else:
            await cursor.execute("UPDATE average SET sum=?, amount=? WHERE id=?",
                           (rate_rows[0] + rate, rate_rows[1] + 1, user_id,))
        await async_connection.commit()


async def get_avg_stats(user_id: int):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM average WHERE id=?", (user_id,))
        rate_rows = await cursor.fetchone()
        if rate_rows is None:
            await add_new_user_to_average(user_id)
            await cursor.execute("SELECT * FROM average WHERE id=?", (user_id,))
            rate_rows = await cursor.fetchone()
        return rate_rows


async def get_large_overshoot():
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM average")
        rows = await cursor.fetchone()
        await cursor.execute('''SELECT DISTINCT overshoot
                          FROM average
                          ORDER BY overshoot DESC''')
        second_largest_overshoot = (await cursor.fetchall())[int(0.25 * len(rows)) - 1][0]
        return second_largest_overshoot


async def get_large_last_incel():
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM average")
        rows = await cursor.fetchone()
        await cursor.execute('''SELECT DISTINCT afk_times
                          FROM average
                          ORDER BY afk_times DESC''')
        second_largest_last_incel = (await cursor.fetchall())[int(0.25 * len(rows)) - 1][0]
        return second_largest_last_incel



async def change_avg_rate(user_id: int, sum: int, amount: int):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT sum, amount FROM average WHERE id=?", (user_id,))
        rate_rows = await cursor.fetchone()
        if rate_rows is None:
            await cursor.execute("INSERT INTO average (id, sum, amount) VALUES (?, ?, ?)",
                           (user_id, sum, amount))
        else:
            await cursor.execute("UPDATE average SET sum=?, amount=? WHERE id=?",
                           (sum, amount, user_id,))
        await async_connection.commit()


async def get_last():
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT MAX(id) FROM sluts_info")
        rows = (await cursor.fetchone())[0]
        if rows is None:
            return 0
        return rows


async def get_min():
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT MIN(id) FROM sluts_info")
        rows = (await cursor.fetchone())[0]
        if rows is None:
            return 0
        if rows == 1:
            return 0
        return rows


async def add_photo_id(num, file_id, username):
    if num == 0:
        return 'error'
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("INSERT INTO sluts_info (id, file_id, origin) VALUES (?, ?, ?)", (num, file_id, username))
        await async_connection.commit()


async def add_rate(num, username, rate):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT votes FROM sluts_info WHERE id=?", (num,))
        votes_rows = (await cursor.fetchone())[0]
        votes = {} if votes_rows is None else json.loads(votes_rows)
        votes[username] = rate
        votes = json.dumps(votes)
        await cursor.execute("UPDATE sluts_info SET votes=? WHERE id=?", (votes, num,))
        await async_connection.commit()


async def get_rate(num, user_id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        username = await get_username_by_id(user_id)
        await cursor.execute("SELECT votes FROM sluts_info WHERE id=?", (num,))
        votes_rows = (await cursor.fetchone())[0]
        votes = {} if votes_rows is None else json.loads(votes_rows)
        if len(votes) == 0 or username not in votes:
            return 0
        return votes[username]


async def add_note(num, note):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("UPDATE sluts_info SET note=? WHERE id=?", (note, num,))
        await async_connection.commit()


async def get_note_sql(num):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT note FROM sluts_info WHERE id=?", (num,))
        note = (await cursor.fetchone())[0]
        return note


async def async_get_note_sql(num):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT note FROM sluts_info WHERE id=?", (num,))
        note = await cursor.fetchone()
        if note:
            return note[0]
        return None


async def get_origin(num):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT origin FROM sluts_info WHERE id=?", (num,))
        row = await cursor.fetchone()
        if row:
            return row[0]
        return None  # Возвращаем None, если результат запроса пустой


async def get_votes(num):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT votes FROM sluts_info WHERE id=?", (num,))
        votes_tuple = (await cursor.fetchone())[0]
        if votes_tuple is None:
            return {}
        votes: Dict = json.loads(votes_tuple)
        return votes


async def get_photo_id_by_id(id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT file_id FROM sluts_info WHERE id=?", (id,))
        photo_id = await cursor.fetchone()
        if photo_id:
            return photo_id[0]
        return photo_id


async def get_async_connection():
    async_connection = await aiosqlite.connect(db)
    return async_connection


async def async_get_photo_id_by_id(id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT file_id, votes FROM sluts_info WHERE id=?", (id,))
        result = await cursor.fetchone()
        if result:
            return (result[0], json.loads(result[1]))
        return (None, {})


async def max_photo_id_among_all(username):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT MAX(id) FROM sluts_info WHERE origin!=?", (username,))
        photo_id = (await cursor.fetchone())[0]
        return photo_id


async def max_photo_id_by_username(username):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT MAX(id) FROM sluts_info WHERE origin=?", (username,))
        photo_id = (await cursor.fetchone())[0]
        return photo_id


async def len_photos_by_username(username):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT id FROM sluts_info WHERE origin=?", (username,))
        ln = await cursor.fetchall()
        return len(ln)


async def get_sluts_db():
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM sluts_info")
        rows = await cursor.fetchall()
        return rows


async def delete_row_in_average(user_id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("DELETE FROM average WHERE id=?", (user_id,))
        await async_connection.commit()
        if cursor.rowcount == 0:
            return 0
        return 1


def print_db():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sluts_info")
    rows = cursor.fetchall()
    cnt = 0
    for row in rows:
        print(row)
    conn.close()


def print_average():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM average")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()



if __name__ == '__main__':
    # get_last()
    print_db()
    #print_average()
    # cursor.execute("SELECT * FROM results")
    # rows = cursor.fetchall()
    # for row in rows:
    #     print(row)
    # print(max_photo_id('nklnkk'))
    # print(len_photos_by_username('nklnkk'))