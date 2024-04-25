import random
import asyncio
import cv2
import numpy as np
from scipy.spatial import KDTree
import sqlite3
import json
import aiosqlite
from db_paths import db_paths

conn = sqlite3.connect(db_paths['emoji'])
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS emoji 
                  (id INTEGER PRIMARY KEY, emoji TEXT, colors TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS emotions 
                  (id INTEGER PRIMARY KEY, emoji TEXT, Red BOOL, Green BOOL, Blue BOOL, Yellow BOOL, Purple BOOL, Turquoise BOOL, DarkGreen BOOL, DarkDarkGreen BOOL, DarkDarkRed BOOL, DarkBlue BOOL, Cyan BOOL, DarkYellow BOOL, DarkTurquoise BOOL, White BOOL, Pink BOOL, Vinous BOOL, Magenta BOOL, Lime BOOL, Gold BOOL, LightPink BOOL, DenseWood BOOL, Chocolate BOOL, Orange BOOL, Black BOOL, Beige BOOL, Grey BOOL)''')

color_names: dict = {
    (240, 0, 0): 'Red',
    (0, 200, 0): 'Green',
    (0, 0, 240): 'Blue',
    (240, 240, 0): 'Yellow',
    (240, 0, 240): 'Purple',
    (0, 240, 240): 'Turquoise',
    (0, 128, 0): 'DarkGreen',
    (0, 80, 0): 'DarkDarkGreen',
    (80, 0, 0): 'DarkDarkRed',
    (0, 0, 128): 'DarkBlue',
    (135, 206, 250): "Cyan",
    (128, 128, 0): 'DarkYellow',
    (0, 128, 128): 'DarkTurquoise',
    (255, 255, 255): 'White',
    (255, 0, 150): 'Pink',
    (128, 0, 0): 'Vinous',
    (128, 0, 128): 'Magenta',
    (0, 255, 0): 'Lime',
    (255, 215, 0): 'Gold',
    (255, 182, 193): 'LightPink',
    (222, 184, 135): 'DenseWood',
    (210, 105, 30): 'Chocolate',
    (250, 128, 90): 'Orange',
    (0, 0, 0): 'Black',
    (240, 222, 197): 'Beige',
    (128, 128, 128): 'Grey',
    (82, 125, 178): 'Cyan',
    (255, 140, 0): 'Orange'
}
interesting = set(color_names.values()) - {'Black', 'Beige', 'DarkYellow', 'DarkDarkGreen', 'White', 'DarkYellow', 'Vinous', 'Grey', 'DenseWood'}

palette = list(color_names.keys())
palette_tree = KDTree(palette)


async def search_emoji_by_colors(colors):
    conn = await get_async_connection()
    async with conn.cursor() as cursor:
        resultM = []
        for i in colors:
            if i in interesting:
                query = f"SELECT emoji FROM emotions WHERE {i}=1"
                await cursor.execute(query)
                result = await cursor.fetchall()
                if result:
                    resultM += result
                    return random.choice(resultM)[0]
        for i in range(len(colors), 0, -1):
            query = "SELECT emoji FROM emotions WHERE "
            for j, color in enumerate(colors[:i]):
                query += f"{color} = 1 AND "
            query = query[:-5]  # Убираем последний "AND"
            await cursor.execute(query)
            result = await cursor.fetchall()
            if result:
                resultM += result
        if len(resultM) != 0:
            return random.choice(resultM)[0]
        else:
            sql_query = 'SELECT emoji FROM emotions ORDER BY RANDOM() LIMIT 1;'
            await cursor.execute(sql_query)
            random_emoji = await cursor.fetchone()
            return random_emoji[0]

async def get_async_connection():
    async_connection = await aiosqlite.connect(db_paths['emoji'])
    return async_connection


def add_color_emoji(id, color):
    cursor.execute("SELECT colors FROM emoji WHERE id=?", (id,))
    colors = cursor.fetchone()[0]
    if colors is None or colors == '':
        colors = str(color)
    else:
        colors = set(map(int, colors.split(',')))
        colors.add(color)
        colors = ', '.join(map(str, colors))
    cursor.execute("UPDATE emoji SET colors=? WHERE id=?", (colors, id,))
    conn.commit()


def delete_color_emoji(id, color: int):
    cursor.execute("SELECT colors FROM emoji WHERE id=?", (id,))
    colors = cursor.fetchone()[0]
    if not (colors is None or colors == ''):
        colors = set(map(int, colors.split(',')))
        colors.remove(color)
        colors = ', '.join(map(str, colors))
        cursor.execute("UPDATE emoji SET colors=? WHERE id=?", (colors, id,))
        conn.commit()


def add_new_emoji(emoji: str):
    cursor.execute("SELECT MAX(id) FROM emoji")
    max_id = cursor.fetchone()[0]
    if max_id is None:
        max_id = 0
    cursor.execute("INSERT INTO emoji (id, emoji) VALUES (?, ?)", (max_id + 1, emoji))
    conn.commit()
    return max_id + 1


def get_colors_emoji(emoji: str):
    emoji_id = get_id_emoji(emoji)
    cursor.execute("SELECT colors FROM emoji WHERE id=?", (emoji_id,))
    colors = cursor.fetchone()[0]
    if colors is None or colors == '':
        return set()
    colors = set(map(int, colors.split(',')))
    return colors


def get_id_emoji(emoji: str):
    cursor.execute("SELECT id FROM emoji WHERE emoji=?", (emoji,))
    id = cursor.fetchone()
    if id is None or id[0] is None:
        id = add_new_emoji(emoji)
        return id
    return id[0]


def map_color_to_palette(rgb_color):
    _, index = palette_tree.query(rgb_color)
    closest_color = palette[index]
    return closest_color, color_names[closest_color]


def get_colors(path):
    image = cv2.imread(path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    scale_percent = 50
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    d: dict = {}
    pixels = np.reshape(image, (-1, 3))
    color_counts = list(map(tuple, pixels))
    for pixel in color_counts:
        color = pixel
        closest_color, color_name = map_color_to_palette(color)
        d[closest_color] = d.get(closest_color, 0) + 1
    d: tuple = sorted(d.items(), key=lambda x: x[1], reverse=True)
    d = ((i[0], i[1] / len(color_counts) * 100) for i in d)
    return d


if __name__ == '__main__':
    colors = list(get_colors('image5.png'))
    print(colors)
    emoji_colors = colors[:5]
    if emoji_colors[0][1] > 50:
        emoji_colors = [color_names[emoji_colors[0][0]]]
    else:
        emoji_colors = [color_names[i[0]] for i in emoji_colors if i[1] > 7]
        if 'Grey' in emoji_colors[:3] and 'Black' in emoji_colors[:3]:
            emoji_colors = ['Grey']
    print(emoji_colors)
    c = asyncio.run(search_emoji_by_colors(emoji_colors))
    print(c)

    # for i in range(1, 283):
    #     cursor.execute("SELECT * FROM emoji WHERE id=?", (i,))
    #     result = cursor.fetchone()
    #     colors = result[2]
    #     if colors is None or colors == '':
    #         colors = [i, result[1]] + [False] * 25 + [True]
    #     else:
    #         colors2 = set(map(int, colors.split(',')))
    #         colors = [i, result[1]]
    #         for j in range(26):
    #             if (j+1) in colors2:
    #                 colors.append(True)
    #             else:
    #                 colors.append(False)
    #     cursor.execute("INSERT INTO emotions (id, emoji, Red  , Green  , Blue  , Yellow  , Purple  , Turquoise  , DarkGreen  , DarkDarkGreen  , DarkDarkRed  , DarkBlue  , Cyan  , DarkYellow  , DarkTurquoise  , White  , Pink  , Vinous  , Magenta  , Lime  , Gold  , LightPink  , DenseWood  , Chocolate  , Orange  , Black  , Beige, Grey) VALUES (?, ?, ?, ?,?, ?, ?, ?,?, ?, ?, ?,?, ?, ?, ?,?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?)",
    #                    tuple(colors))
    #     conn.commit()
    # cursor.execute("SELECT * FROM emotions")
    # rows = cursor.fetchall()
    # for row in rows:
    #     print(row)
