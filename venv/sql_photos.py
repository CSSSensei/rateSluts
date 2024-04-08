import datetime
import sqlite3
import json
from typing import Dict

conn = sqlite3.connect('slutsDB.db')
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS sluts_info 
                  (id INT PRIMARY KEY, note TEXT, votes TEXT, file_id TEXT, origin TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS average 
                  (id INT PRIMARY KEY, sum INT, amount INT, overshoot INT, hit INT, hit_amount INT, afk_times INT, last_upd INT, total_time INT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS results
                  (id INT PRIMARY KEY, photo TEXT, rate FLOAT, user_id INT)''')


def add_not_incel_photo(num, photo, user_id, rate=-1):
    cursor.execute("INSERT INTO results (id, photo, rate, user_id) VALUES (?, ?, ?, ?)", (num, photo, rate, user_id))
    conn.commit()


def add_new_user_to_average(user_id):
    cursor.execute(
        "INSERT INTO average (id, sum, amount, overshoot, hit, hit_amount, afk_times, last_upd, total_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, 0, 0, 0, 0, 0, 0, 0, 0))
    conn.commit()


def get_last_upd(user_id: int):
    cursor.execute("SELECT last_upd FROM average WHERE id=?", (user_id,))
    last_upd = cursor.fetchone()
    if last_upd is None:
        add_new_user_to_average(user_id)
        return 0
    return last_upd[0]


def increment_time(user_id: int, time_delta: int, current_time: int):
    cursor.execute("SELECT total_time FROM average WHERE id=?", (user_id,))
    total_time = cursor.fetchone()
    if total_time is None:
        add_new_user_to_average(user_id)
        total_time = 0
    else:
        total_time = total_time[0]
    cursor.execute("UPDATE average SET total_time=?, last_upd=? WHERE id=?", (total_time + time_delta, current_time, user_id))
    conn.commit()


def change_last_update(user_id: int, current_time: int):
    cursor.execute("UPDATE average SET last_upd=? WHERE id=?", (current_time, user_id))
    conn.commit()


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


def get_not_incel_rate(num):
    cursor.execute("SELECT rate FROM results WHERE id=?", (num,))
    rate = cursor.fetchone()
    return None if rate is None else rate[0]


def add_overshoot(user_id: int):
    cursor.execute("SELECT overshoot FROM average WHERE id=?", (user_id,))
    rows = cursor.fetchone()
    if rows is None:
        add_new_user_to_average(user_id)
        rows = 0
    else:
        rows = rows[0]
    cursor.execute("UPDATE average SET overshoot=? WHERE id=?", (rows + 1, user_id))
    conn.commit()


def add_hit(user_id: int, hit: int = 0):
    cursor.execute("SELECT hit_amount FROM average WHERE id=?", (user_id,))
    rows = cursor.fetchone()
    if rows is None:
        add_new_user_to_average(user_id)
        rows = 0
    else:
        rows = rows[0]
    cursor.execute("UPDATE average SET hit_amount=? WHERE id=?", (rows + 1, user_id))
    conn.commit()
    if hit != 0:
        cursor.execute("SELECT hit FROM average WHERE id=?", (user_id,))
        hit_num = cursor.fetchone()[0]
        cursor.execute("UPDATE average SET hit=? WHERE id=?", (hit_num + 1, user_id))
        conn.commit()


def add_afk(user_id: int):
    cursor.execute("SELECT afk_times FROM average WHERE id=?", (user_id,))
    rows = cursor.fetchone()
    if rows is None:
        add_new_user_to_average(user_id)
        rows = 0
    else:
        rows = rows[0]
    cursor.execute("UPDATE average SET afk_times=? WHERE id=?", (rows + 1, user_id))
    conn.commit()


def add_rate_not_incel(num, rate):
    cursor.execute("UPDATE results SET rate=? WHERE id=?", (rate, num))
    conn.commit()


def get_avgs_not_incel(user_id):
    cursor.execute("SELECT rate FROM results WHERE user_id=?", (user_id,))
    rate = cursor.fetchall()
    return rate


def add_rate_to_avg(user_id: int, rate: int):
    cursor.execute("SELECT sum, amount FROM average WHERE id=?", (user_id,))
    rate_rows = cursor.fetchone()
    if rate_rows is None:
        cursor.execute("INSERT INTO average (id, sum, amount) VALUES (?, ?, ?)",
                       (user_id, rate, 1))
        conn.commit()
    else:
        cursor.execute("UPDATE average SET sum=?, amount=? WHERE id=?",
                       (rate_rows[0] + rate, rate_rows[1] + 1, user_id,))
        conn.commit()


def get_avg_stats(user_id: int):
    cursor.execute("SELECT * FROM average WHERE id=?", (user_id,))
    rate_rows = cursor.fetchone()
    if rate_rows is None:
        add_new_user_to_average(user_id)
        cursor.execute("SELECT * FROM average WHERE id=?", (user_id,))
        rate_rows = cursor.fetchone()
    return rate_rows


def get_large_overshoot():
    cursor.execute("SELECT * FROM average")
    rows = cursor.fetchone()
    cursor.execute('''SELECT DISTINCT overshoot
                      FROM average
                      ORDER BY overshoot DESC''')
    second_largest_overshoot = cursor.fetchall()[int(0.25 * len(rows)) - 1][0]
    return second_largest_overshoot


def get_large_last_incel():
    cursor.execute("SELECT * FROM average")
    rows = cursor.fetchone()
    cursor.execute('''SELECT DISTINCT afk_times
                      FROM average
                      ORDER BY afk_times DESC''')
    second_largest_last_incel = cursor.fetchall()[int(0.25 * len(rows)) - 1][0]
    return second_largest_last_incel



def change_avg_rate(user_id: int, sum: int, amount: int):
    cursor.execute("SELECT sum, amount FROM average WHERE id=?", (user_id,))
    rate_rows = cursor.fetchone()
    if rate_rows is None:
        cursor.execute("INSERT INTO average (id, sum, amount) VALUES (?, ?, ?)",
                       (user_id, sum, amount))
        conn.commit()
    else:
        cursor.execute("UPDATE average SET sum=?, amount=? WHERE id=?",
                       (sum, amount, user_id,))
        conn.commit()


def get_last():
    cursor.execute("SELECT MAX(id) FROM sluts_info")
    rows = cursor.fetchone()[0]
    if rows is None:
        return 0
    return rows


def get_min():
    cursor.execute("SELECT MIN(id) FROM sluts_info")
    rows = cursor.fetchone()[0]
    if rows is None:
        return 0
    if rows == 1:
        return 0
    return rows


def add_photo_id(num, file_id, username):
    if num == 0:
        return 'error'
    cursor.execute("INSERT INTO sluts_info (id, file_id, origin) VALUES (?, ?, ?)", (num, file_id, username))
    conn.commit()


def add_rate(num, username, rate):
    cursor.execute("SELECT votes FROM sluts_info WHERE id=?", (num,))
    votes_rows = cursor.fetchone()[0]
    votes = {} if votes_rows is None else json.loads(votes_rows)
    votes[username] = rate
    votes = json.dumps(votes)
    cursor.execute("UPDATE sluts_info SET votes=? WHERE id=?", (votes, num,))
    conn.commit()


def add_note(num, note):
    cursor.execute("UPDATE sluts_info SET note=? WHERE id=?", (note, num,))
    conn.commit()


def get_note_sql(num):
    cursor.execute("SELECT note FROM sluts_info WHERE id=?", (num,))
    note = cursor.fetchone()[0]
    return note


def get_origin(num):
    cursor.execute("SELECT origin FROM sluts_info WHERE id=?", (num,))
    origin = cursor.fetchone()[0]
    return origin


def get_votes(num):
    cursor.execute("SELECT votes FROM sluts_info WHERE id=?", (num,))
    votes_tuple = cursor.fetchone()[0]
    if votes_tuple is None:
        return {}
    votes: Dict = json.loads(votes_tuple)
    return votes


def get_photo_id_by_id(id):
    cursor.execute("SELECT file_id FROM sluts_info WHERE id=?", (id,))
    photo_id = cursor.fetchone()[0]
    return photo_id


def max_photo_id_among_all(username):
    cursor.execute("SELECT MAX(id) FROM sluts_info WHERE origin!=?", (username,))
    photo_id = cursor.fetchone()[0]
    return photo_id


def max_photo_id_by_username(username):
    cursor.execute("SELECT MAX(id) FROM sluts_info WHERE origin=?", (username,))
    photo_id = cursor.fetchone()[0]
    return photo_id


def len_photos_by_username(username):
    cursor.execute("SELECT id FROM sluts_info WHERE origin=?", (username,))
    ln = cursor.fetchall()
    return len(ln)


def get_sluts_db():
    cursor.execute("SELECT * FROM sluts_info")
    rows = cursor.fetchall()
    return rows


def delete_row_in_average(user_id):
    cursor.execute("DELETE FROM average WHERE id=?", (user_id,))
    conn.commit()
    if cursor.rowcount == 0:
        return 0
    return 1


def print_db():
    cursor.execute("SELECT * FROM sluts_info")
    rows = cursor.fetchall()
    cnt = 0
    for row in rows:
        print(row)
        cnt+=1
        if cnt == 100:
            break


def print_average():
    cursor.execute("SELECT * FROM average")
    rows = cursor.fetchall()
    for row in rows:
        print(row)



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