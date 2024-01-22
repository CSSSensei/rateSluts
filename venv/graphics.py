import sqlite3
import json
import matplotlib.pyplot as plt
from Color2 import color_calculate
from matplotlib.animation import FuncAnimation


def get_statistics(username):
    # Подключаемся к базе данных
    conn = sqlite3.connect('slutsDB.db')
    cursor = conn.cursor()

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

    averages = averages[-200:]
    colors = [color_calculate(avg) for avg in averages]
    # Создаем столбчатую диаграмму с разноцветными столбцами
    if len(averages) >= 100:
        plt.figure(figsize=(6 * len(averages) / 100, 5))

    plt.bar(range(len(averages)), averages, color=colors, width=1)
    plt.title(f'@{username}')
    plt.xlabel('Record Number')
    plt.ylabel('Average')
    plt.savefig(f'myplot_{username}.png')
    # Закрываем соединение с базой данных
    conn.close()
    plt.clf()

    plt.plot(averages)
    plt.title(f'@{username}')
    plt.xlabel('Record Number')
    plt.ylabel('Average')
    plt.savefig(f'myplot_{username}2.png')
    plt.clf()

def new_func(username, averages):
    x = range(len(averages))
    y = averages
    colors = [color_calculate(avg) for avg in averages]

    plt.scatter(x, y, c=colors)
    plt.title(f'@{username} - Average Ratings')
    plt.xlabel('Record Number')
    plt.ylabel('Average Rating')

    plt.savefig(f'myplot_{username}_scatter.png')
    plt.clf()
    #

    labels = ['Positive', 'Neutral', 'Negative']
    sizes = [len([i for i in averages if i>6]), len([i for i in averages if 4<=i<=6]), len([i for i in averages if i<4])]
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    explode = (0.1, 0, 0)  # "взрыв" первого сектора

    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
    plt.title('Sentiment Analysis')

    plt.savefig(f'myplot_{username}_pie.png')
    plt.clf()

    #

    fig, ax = plt.subplots()
    ax.set_xlim(0, len(averages) + 5)
    ax.set_ylim(0, 12)  # Обновляю ограничение по y

    # Создаем пустой график, который будет обновляться с каждым кадром
    line, = ax.plot([], [], color='blue', linewidth=2)

    def update(frame):
        ax.cla()  # Очищаем предыдущий график
        ax.set_xlim(0, len(averages) + 5)
        ax.set_ylim(0, 12)  # Обновляем ограничение по y

        # Отображаем только данные до текущего кадра
        ax.plot(averages[:frame], color='blue', linewidth=2)  # Исправляю использование цвета

        ax.set_title(f'@{username}')
        ax.set_xlabel('Record Number')
        ax.set_ylabel('Average')

    # Создаем анимацию
    anim = FuncAnimation(fig, update, frames=len(averages), interval=200)

    # Сохраняем анимацию в файл
    anim.save(f'myplot_{username}_animation.gif', writer='imagemagick')



