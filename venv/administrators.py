import datetime
import sqlite3
import json
import time
from typing import Dict

conn = sqlite3.connect('admins.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS admins_info 
                  (id INTEGER PRIMARY KEY, active BOOL, trigger TEXT, day_of_week TEXT,
                  hour TEXT, minute TEXT, groups_to_moderate TEXT, mode INTEGER, extra2 TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS group_parser 
                  (id INTEGER PRIMARY KEY, group_name TEXT , active BOOL, top_likes BOOL,
                  photo_amount INTEGER, time_delta TEXT, last_update INTEGER)''')
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


def get_admins():
    cursor.execute("SELECT id FROM admins_info WHERE active=True")
    rows = cursor.fetchall()
    return set(row[0] for row in rows)


def get_message_to_delete(user_id):
    cursor.execute("SELECT trigger FROM admins_info WHERE id=?", (user_id,))
    rows = cursor.fetchone()[0]
    if rows == '-1':
        return None
    return rows


def set_message_to_delete(user_id, message_id: str):
    cursor.execute("UPDATE admins_info SET trigger=? WHERE id=?", (message_id, user_id,))
    conn.commit()


def set_admin(user_id):
    cursor.execute("SELECT * FROM admins_info WHERE id=?", (user_id,))
    rows = cursor.fetchall()
    if not rows:
        cursor.execute("INSERT INTO admins_info (id, active, trigger, day_of_week, hour, minute, mode) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, True, '-1', '1, 2, 3, 4, 5, 6, 7', '20', '00', 1))
        conn.commit()

    else:
        cursor.execute("UPDATE admins_info SET active=? WHERE id=?", (True, user_id,))
        conn.commit()


def add_to_queue_group_photo(user_id: int, num: str):
    cursor.execute("SELECT extra2 FROM admins_info WHERE id=?", (user_id,))
    queue = cursor.fetchone()
    if queue is None or queue[0] == '' or queue[0] is None:
        queue = num
    else:
        queue = set(queue[0].split(', '))
        queue.add(num)
        queue = ', '.join(queue)
    cursor.execute("UPDATE admins_info SET extra2=? WHERE id=?", (queue, user_id,))
    conn.commit()


def get_admins_queue(user_id: int):
    cursor.execute("SELECT extra2 FROM admins_info WHERE id=?", (user_id,))
    queue = cursor.fetchone()
    if queue is None or queue[0] == '' or queue[0] is None:
        return set()
    return set(queue[0].split(', '))


def remove_from_admins_queue(user_id, num):
    if num==0:
        cursor.execute("UPDATE admins_info SET extra2=? WHERE id=?", (None, user_id,))
        conn.commit()
        return
    cursor.execute("SELECT extra2 FROM admins_info WHERE id=?", (user_id,))
    queue = cursor.fetchone()
    if queue is None or queue[0] == '' or queue[0] is None:
        return
    else:
        queue = set(queue[0].split(', '))
        if num in queue:
            queue.remove(num)
            if len(queue) == 0:
                queue = None
                cursor.execute("UPDATE admins_info SET extra2=? WHERE id=?", (queue, user_id,))
                conn.commit()
                return
        queue = ', '.join(map(str, queue))
    cursor.execute("UPDATE admins_info SET extra2=? WHERE id=?", (queue, user_id,))
    conn.commit()


def chill_mode(user_id):
    cursor.execute("SELECT * FROM admins_info WHERE id=?", (user_id,))
    rows = cursor.fetchall()
    if not rows:
        cursor.execute("INSERT INTO admins_info (id, active, mode) VALUES (?, ?, ?)",
                       (user_id, True, 2))
        conn.commit()
    else:
        cursor.execute("UPDATE admins_info SET mode=? WHERE id=?", (2, user_id,))
        conn.commit()


def default_mode(user_id):
    cursor.execute("SELECT * FROM admins_info WHERE id=?", (user_id,))
    rows = cursor.fetchall()
    if not rows:
        cursor.execute("INSERT INTO admins_info (id, active, mode) VALUES (?, ?, ?)",
                       (user_id, True, 1))
        conn.commit()
    else:
        cursor.execute("UPDATE admins_info SET mode=? WHERE id=?", (1, user_id,))
        conn.commit()


def set_inactive(user_id: int):
    cursor.execute("SELECT * FROM admins_info WHERE id=?", (user_id,))
    rows = cursor.fetchall()
    if not rows:
        cursor.execute(
            "INSERT INTO admins_info (id, active, trigger, day_of_week, hour, minute, mode) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, False, '-1', '1, 2, 3, 4, 5, 6, 7', '20', '00', 1))
        conn.commit()

    else:
        cursor.execute("UPDATE admins_info SET active=? WHERE id=?", (False, user_id,))
        conn.commit()


def get_settings(user_id: int):
    cursor.execute("SELECT * FROM admins_info WHERE id=?", (user_id,))
    rows = cursor.fetchone()
    return rows


def get_weekdays(user_id: int):
    cursor.execute("SELECT day_of_week FROM admins_info WHERE id=?", (user_id,))
    rows = cursor.fetchone()
    if rows is None or rows[0] is None:
        return set()
    weekdays = set(map(int, rows[0].split(',')))
    return weekdays


def change_weekdays(user_id: int, day: int):
    cursor.execute("SELECT day_of_week FROM admins_info WHERE id=?", (user_id,))
    rows = cursor.fetchone()
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
        cursor.execute("UPDATE admins_info SET day_of_week=NULL WHERE id=?", (user_id,))
    else:
        cursor.execute("UPDATE admins_info SET day_of_week=? WHERE id=?", (weekdays, user_id,))
    conn.commit()


def get_group_domain(group_id: int):
    cursor.execute("SELECT group_name FROM group_parser WHERE id=?", (group_id,))
    domain = cursor.fetchone()
    return domain[0] if domain is not None else None


def get_group_sets(group_id: int):
    cursor.execute("SELECT * FROM group_parser WHERE id=?", (group_id,))
    rows = cursor.fetchone()
    return rows


def send_photos_by_id(num: int):
    cursor.execute("SELECT * FROM group_photos WHERE id=?", (num,))
    rows = cursor.fetchone()
    return rows


def get_active_groups():
    cursor.execute("SELECT id FROM group_parser WHERE active=?", (True,))
    rows = cursor.fetchall()
    return set(i[0] for i in rows) if rows is not None else None


def get_last_group():
    cursor.execute("SELECT MAX(id) FROM group_parser")
    rows = cursor.fetchone()
    if rows is None:
        return 0
    return rows[0] if rows[0] is not None else 0


def switch_active(group_id: int):
    cursor.execute("SELECT active FROM group_parser WHERE id=?", (group_id,))
    active = cursor.fetchone()[0]
    cursor.execute("UPDATE group_parser SET active=? WHERE id=?", (not active, group_id,))
    conn.commit()


def switch_top_likes(group_id: int):
    cursor.execute("SELECT top_likes FROM group_parser WHERE id=?", (group_id,))
    top_likes = cursor.fetchone()[0]
    cursor.execute("UPDATE group_parser SET top_likes=? WHERE id=?", (not top_likes, group_id,))
    conn.commit()


def change_amount(group_id: int, photo_amount: int):
    cursor.execute("UPDATE group_parser SET photo_amount=? WHERE id=?", (photo_amount, group_id,))
    conn.commit()


def change_date(group_id: int, date: int):
    cursor.execute("UPDATE group_parser SET time_delta=? WHERE id=?", (date, group_id,))
    conn.commit()


def change_hour(user_id: int, hour: int):
    cursor.execute("UPDATE admins_info SET hour=? WHERE id=?", (str(hour), user_id,))
    conn.commit()


def change_minute(user_id: int, minute: str):
    cursor.execute("UPDATE admins_info SET minute=? WHERE id=?", (minute, user_id,))
    conn.commit()


def add_group(user_id: int, domain: str):
    cursor.execute("SELECT groups_to_moderate FROM admins_info WHERE id=?", (user_id,))
    groups = cursor.fetchone()[0]
    num = get_last_group() + 1
    if groups is None or groups == '':
        groups = str(num)
    else:
        groups = set(map(int, groups.split(',')))
        for id in groups:
            if domain == get_group_domain(id):
                return -1, id
        groups.add(num)
        groups = ', '.join(map(str, groups))
    cursor.execute("UPDATE admins_info SET groups_to_moderate=? WHERE id=?", (groups, user_id,))
    conn.commit()
    cursor.execute("INSERT INTO group_parser (id, group_name, active, top_likes, photo_amount, time_delta, last_update) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (num, domain, True, True, 3, 5, 0))
    conn.commit()
    return num, num


def update_time(group_id: int, time_now=None):
    if time_now is None:
        time_now = int(time.time())
    cursor.execute("UPDATE group_parser SET last_update=? WHERE id=?", (time_now, group_id))
    conn.commit()


def delete_group(group_id: int, user_id: int):
    cursor.execute('DELETE FROM group_parser WHERE id=?', (group_id,))
    conn.commit()
    cursor.execute("SELECT groups_to_moderate FROM admins_info WHERE id=?", (user_id,))
    groups = set(map(int, cursor.fetchone()[0].split(',')))
    groups.remove(group_id)
    if len(groups) == 0:
        groups = None
    else:
        groups = ', '.join(map(str, groups))
    cursor.execute("UPDATE admins_info SET groups_to_moderate=? WHERE id=?", (groups, user_id,))
    conn.commit()


def last_group_photo_id():
    cursor.execute("SELECT MAX(id) FROM group_photos")
    rows = cursor.fetchone()[0]
    if rows is None:
        return 0
    return rows


def add_group_photo(num, origin, caption, url):
    cursor.execute("INSERT INTO group_photos (id, group_name, caption, url) VALUES (?, ?, ?, ?)",
                   (num, origin, caption, url))
    conn.commit()


def get_group_photo_info(num):
    cursor.execute("SELECT * FROM group_photos WHERE id=?", (num,))
    rows = cursor.fetchone()
    return rows


def del_group_photo(num):
    cursor.execute('DELETE FROM group_photos WHERE id=?', (num,))
    conn.commit()


def get_hour(user_id: int):
    cursor.execute("SELECT hour FROM admins_info WHERE id=?", (user_id,))
    rows = cursor.fetchone()
    return int(rows[0])


def set_hour(user_id: int, hour: str):
    cursor.execute("UPDATE admins_info SET hour=? WHERE id=?", (hour, user_id,))
    conn.commit()


def get_minute(user_id: int):
    cursor.execute("SELECT minute FROM admins_info WHERE id=?", (user_id,))
    rows = cursor.fetchone()
    return int(rows[0])


def set_minute(user_id: int, minute: str):
    cursor.execute("UPDATE admins_info SET minute=? WHERE id=?", (minute, user_id,))
    conn.commit()


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
