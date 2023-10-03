import sqlite3
import json
import matplotlib.pyplot as plt


def get_statistics(username):
    # Подключаемся к базе данных
    conn = sqlite3.connect('slutsDB.db')
    cursor = conn.cursor()

    # Выбираем записи с username == 'nklnkk'
    cursor.execute(f"SELECT * FROM sluts_info WHERE origin = '{username}'")
    rows = cursor.fetchall()

    # Создаем списки для хранения данных
    votes = []
    averages = []

    # Извлекаем данные из записей
    for row in rows:
        if row[2] is None:
            continue
        g = json.loads(row[2])
        votes.append(list(g.values())[0])
        averages.append(sum(g.values()) / len(g.keys()))
    # Создаем график среднего значения
    plt.plot(averages)
    plt.title(f'@{username}')
    plt.xlabel('Record Number')
    plt.ylabel('Average')
    plt.savefig(f'myplot_{username}.jpg')
    # Закрываем соединение с базой данных
    conn.close()
    plt.clf()
