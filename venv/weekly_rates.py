import sqlite3
import imagehash
from PIL import Image
import aiosqlite
from vova_function import calculate_separators
from db_paths import db_paths


weekly = db_paths['weekly']
weekly_info = db_paths['weekly_info']
conn = sqlite3.connect(weekly)
cursor = conn.cursor()
conn2 = sqlite3.connect(weekly_info)
cursor2 = conn2.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS weekly
                  (photo_id TEXT PRIMARY KEY, average FLOAT, hash TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS borders
                  (left_border FLOAT, right_border FLOAT)''')

cursor2.execute('''CREATE TABLE IF NOT EXISTS if_send
                  (id INT PRIMARY KEY, weekly_sending BOOl)''')
cursor2.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='public_info'")
table_exists = cursor2.fetchone()

if not table_exists:
    # Если таблицы не существует, создаем таблицу и добавляем значение
    cursor2.execute('''CREATE TABLE IF NOT EXISTS public_info
                      (queue TEXT)''')
    cursor2.execute("INSERT INTO public_info (queue) VALUES (NULL);")
    conn2.commit()
else:
    cursor2.execute('''CREATE TABLE IF NOT EXISTS public_info
                  (queue TEXT)''')
conn2.close()
conn.close()


def get_caption_public(hour):
    if 5 <= hour < 12:
        return "Доброе утро! 🌅☀️"
    elif 12 <= hour < 16:
        return "Добрый день! 🌞🌼"
    elif 16 <= hour < 20:
        return "Хорошего вечера! 🌆🌇"
    elif 20 <= hour < 24:
        return "Добрый вечер! 🌙🌠"
    else:
        return "Спокойной ночи! 🌜🌌"


async def add_to_weekly(id, avg, hash=None):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM weekly WHERE photo_id = ?", (id,))
        existing_row = await cursor.fetchone()

        if existing_row:
            if hash:
                await cursor.execute("UPDATE weekly SET average = ?, hash = ? WHERE photo_id = ?", (avg, hash, id))
            else:
                await cursor.execute("UPDATE weekly SET average = ? WHERE photo_id = ?", (avg, id))
        else:
            await cursor.execute("INSERT INTO weekly (photo_id, average, hash) VALUES (?, ?, ?)", (id, avg, hash))

        await async_connection.commit()


async def update_borders():
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT average FROM weekly WHERE average IS NOT NULL")
        queue_length = await public_queue()
        rows = [i[0] for i in (await cursor.fetchall())[-1000 - queue_length:-queue_length]]
        seps: tuple = calculate_separators(rows)
        await cursor.execute("SELECT left_border from borders")
        border = await cursor.fetchone()
        if border:
            await cursor.execute("UPDATE borders SET left_border = ?, right_border = ?", seps)
        else:
            await cursor.execute("INSERT INTO borders (left_border, right_border) VALUES (?, ?)", seps)
        await async_connection.commit()
        
        
async def get_borders():
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT left_border, right_border from borders")
        borders = await cursor.fetchone()
        if borders is None:
            return (3.0, 7.5)
        return borders

async def get_min_from_public_info():
    async_connection = await get_async_connection2()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT queue FROM public_info")
        queue = await cursor.fetchone()
        if queue is None or queue[0] is None or queue[0] == '':
            return None
        return min(set(map(int, queue[0].split(','))))


async def get_async_connection():
    async_connection = await aiosqlite.connect(weekly)
    return async_connection


async def get_async_connection2():
    async_connection = await aiosqlite.connect(weekly_info)
    return async_connection


async def get_hash_from_db(photo_id):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT hash FROM weekly WHERE photo_id = ?", (photo_id,))
        existing_row = await cursor.fetchone()
        return existing_row[0] if existing_row else None


async def add_to_queue_public_info(num):
    async_connection = await get_async_connection2()
    async with async_connection.cursor() as cursor2:
        await cursor2.execute("SELECT queue FROM public_info")
        queue = await cursor2.fetchone()
        if queue is None or queue[0] is None or queue[0] == '':
            queue = str(num)
        else:
            queue = set(map(int, queue[0].split(',')))
            queue.add(num)
            queue = ', '.join(map(str, queue))
        await cursor2.execute("UPDATE public_info SET queue=?", (queue,))
        await async_connection.commit()


async def delete_from_queue_public_info(num):
    async_connection = await get_async_connection2()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT queue FROM public_info")
        queue = await cursor.fetchone()
        if queue is None or not queue[0]:
            return
        queue = set(map(int, queue[0].split(',')))
        if num in queue:
            queue.remove(num)
            if not queue:
                queue = None
                await cursor.execute("UPDATE public_info SET queue = ? ", (queue,))
                await async_connection.commit()
            else:
                queue_str = ', '.join(map(str, queue))
                await cursor.execute("UPDATE public_info SET queue = ? ", (queue_str,))
                await async_connection.commit()
    await async_connection.close()

async def public_queue():
    async_connection = await get_async_connection2()
    async with async_connection.cursor() as cursor2:
        await cursor2.execute("SELECT * FROM public_info")
        queue = await cursor2.fetchone()
        return len(queue[0].split(','))


async def clear_db():
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute('DELETE FROM weekly;')
        await async_connection.commit()


async def get_weekly_db():
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM weekly WHERE average IS NOT NULL")
        rows = await cursor.fetchall()
        result = {}
        for row in rows:
            avg = row[1]
            if avg <= 2.5:
                key = 0
            elif 2.5 < avg < 4:
                key = 1
            elif 4 <= avg <= 5.5:
                key = 2
            elif 5.5 < avg <= 6.9:
                key = 3
            elif 6.9 < avg < 9:
                key = 4
            else:
                key = 5
            result[key] = [{avg: row[0]}] + result.get(key, [])

        new = {}
        for i, j in result.items():
            sorted_lst = sorted(j, key=lambda x: list(x.keys())[0])
            new[i] = [list(i.values())[0] for i in sorted_lst]
        return dict(sorted(new.items(), reverse=True))


async def weekly_cancel(id):
    async_connection = await get_async_connection2()
    async with async_connection.cursor() as cursor2:
        await cursor2.execute("SELECT id FROM if_send WHERE id=?", (id,))
        row = await cursor2.fetchone()

        if row is not None:
            await cursor2.execute("UPDATE if_send SET weekly_sending=? WHERE id=?", (False, id))
        else:
            await cursor2.execute("INSERT INTO if_send (id, weekly_sending) VALUES (?, ?)", (id, False))

        await async_connection.commit()


async def get_weekly_db_info():
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute("SELECT * FROM weekly")
        rows = await cursor.fetchall()
        return rows


async def get_weekly(id):
    async_connection = await get_async_connection2()
    async with async_connection.cursor() as cursor2:
        await cursor2.execute("SELECT weekly_sending FROM if_send WHERE id=?", (id,))
        row = await cursor2.fetchone()
        if row is None:
            await cursor2.execute("INSERT INTO if_send (id, weekly_sending) VALUES (?, ?)", (id, True))
            return True
        return row[0]


async def weekly_resume(id):
    async_connection = await get_async_connection2()
    async with async_connection.cursor() as cursor2:
        await cursor2.execute("SELECT id FROM if_send WHERE id=?", (id,))
        row = await cursor2.fetchone()
        if row is not None:
            await cursor2.execute("UPDATE if_send SET weekly_sending=? WHERE id=?", (True, id))
        else:
            await cursor2.execute("INSERT INTO if_send (id, weekly_sending) VALUES (?, ?)", (id, True))
        await async_connection.commit()


def percentage_difference(image1, image2):
    hash1 = imagehash.average_hash(Image.open(image1), hash_size=8)
    hash2 = imagehash.average_hash(Image.open(image2), hash_size=8)
    diff = hash1 - hash2
    max_bits = hash1.hash.size ** 2
    percent_diff = (diff / hash1.hash.size) * 100
    return percent_diff


def get_hash(image_path):
    hash = imagehash.average_hash(Image.open(image_path), hash_size=8)
    return str(hash)


def hash_similar(hash1, hash2, threshold=0.03):
    hash1, hash2 = imagehash.hex_to_hash(hash1), imagehash.hex_to_hash(hash2)
    diff = hash1 - hash2
    percent_diff = (diff / hash1.hash.size)
    return percent_diff <= threshold


async def get_similarities(hash):
    async_connection = await get_async_connection()
    async with async_connection.cursor() as cursor:
        await cursor.execute('SELECT photo_id, hash FROM weekly')
        for row in (await cursor.fetchall()):
            link, hash_str = row
            if hash_str is None:
                continue
            if hash_similar(hash_str, hash, threshold=0.03):
                return True
        return False


def print_db(n=2):
    if n == 0 or n == 2:
        cursor.execute("SELECT * FROM weekly")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    if n == 1 or n == 2:
        cursor2.execute("SELECT * FROM if_send")
        rows = cursor2.fetchall()
        for row in rows:
            print(row)


if __name__ == '__main__':
    # print_db(0)
    # cursor2.execute("SELECT * FROM public_info")
    # queue = cursor2.fetchone()
    # print(len(queue[0].split(',')), queue)

    conn = sqlite3.connect(weekly)
    cursor = conn.cursor()
    cursor.execute("SELECT hash FROM weekly WHERE hash is not NULL")
    print(cursor.fetchall())
    conn.close()

