import sqlite3
import imagehash
from PIL import Image
conn = sqlite3.connect('weekly.db')
cursor = conn.cursor()
conn2 = sqlite3.connect('weekly_info.db')
cursor2 = conn2.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS weekly
                  (photo_id TEXT PRIMARY KEY, average FLOAT, hash TEXT)''')

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


def add_to_weekly(id, avg, hash=None):
    cursor.execute("SELECT * FROM weekly WHERE photo_id = ?", (id,))
    existing_row = cursor.fetchone()

    if existing_row:
        if hash:
            cursor.execute("UPDATE weekly SET average = ?, hash = ? WHERE photo_id = ?", (avg, hash, id))
        else:
            cursor.execute("UPDATE weekly SET average = ? WHERE photo_id = ?", (avg, id))
    else:
        cursor.execute("INSERT INTO weekly (photo_id, average, hash) VALUES (?, ?, ?)", (id, avg, hash))

    conn.commit()


def get_min_from_public_info():
    cursor2.execute("SELECT queue FROM public_info")
    queue = cursor2.fetchone()
    if queue is None or queue[0] is None or queue[0] == '':
        return set()
    return min(set(map(int, queue[0].split(','))))


def get_hash_from_db(photo_id):
    cursor.execute("SELECT hash FROM weekly WHERE photo_id = ?", (photo_id,))
    existing_row = cursor.fetchone()
    return existing_row[0]


def add_to_queue_public_info(num):
    cursor2.execute("SELECT queue FROM public_info")
    queue = cursor2.fetchone()
    if queue is None or queue[0] is None or queue[0] == '':
        queue = str(num)
    else:
        queue = set(map(int, queue[0].split(',')))
        queue.add(num)
        queue = ', '.join(map(str, queue))
    cursor2.execute("UPDATE public_info SET queue=?", (queue,))
    conn2.commit()


def delete_from_queue_public_info(num):
    cursor2.execute("SELECT queue FROM public_info")
    queue = cursor2.fetchone()
    if queue is None or queue[0] is None or queue[0] == '':
        return
    else:
        queue = set(map(int, queue[0].split(',')))
        if num in queue:
            queue.remove(num)
            if len(queue) == 0:
                queue = None
                cursor2.execute("UPDATE public_info SET queue=? ", (queue,))
                conn2.commit()
                return
        queue = ', '.join(map(str, queue))
    cursor2.execute("UPDATE public_info SET queue=?", (queue,))
    conn2.commit()

def public_queue():
    cursor2.execute("SELECT * FROM public_info")
    queue = cursor2.fetchone()
    return len(queue[0].split(','))


def clear_db():
    cursor.execute('DELETE FROM weekly;')
    conn.commit()


def get_weekly_db():
    cursor.execute("SELECT * FROM weekly WHERE average IS NOT NULL")
    rows = cursor.fetchall()
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


def weekly_cancel(id):
    cursor2.execute("SELECT id FROM if_send WHERE id=?", (id,))
    row = cursor2.fetchone()

    if row is not None:
        cursor2.execute("UPDATE if_send SET weekly_sending=? WHERE id=?", (False, id))
    else:
        cursor2.execute("INSERT INTO if_send (id, weekly_sending) VALUES (?, ?)", (id, False))

    conn2.commit()


def get_weekly_db_info():
    cursor.execute("SELECT * FROM weekly")
    rows = cursor.fetchall()
    return rows


def get_weekly(id):
    cursor2.execute("SELECT weekly_sending FROM if_send WHERE id=?", (id,))
    row = cursor2.fetchone()
    if row is None:
        cursor2.execute("INSERT INTO if_send (id, weekly_sending) VALUES (?, ?)", (id, True))
        return True
    return row[0]


def weekly_resume(id):
    cursor2.execute("SELECT id FROM if_send WHERE id=?", (id,))
    row = cursor2.fetchone()
    if row is not None:
        cursor2.execute("UPDATE if_send SET weekly_sending=? WHERE id=?", (True, id))
    else:
        cursor2.execute("INSERT INTO if_send (id, weekly_sending) VALUES (?, ?)", (id, True))
    conn2.commit()


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


def get_similarities(hash):
    for row in cursor.execute('SELECT photo_id, hash FROM weekly'):
        link, hash_str = row
        if hash_str is None:
            continue
        if hash_similar(hash_str, hash, threshold=0.05):
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
    print_db(0)
    # cursor2.execute("SELECT * FROM public_info")
    # queue = cursor2.fetchone()
    # print(len(queue[0].split(',')), queue)
