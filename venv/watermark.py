from PIL import Image, ImageDraw, ImageFont
from math import sqrt
import os

def watermark(path: str, rt: int, hsh: str):
    def choose_color(*points: tuple) -> tuple:
        nonlocal img
        w, b = (255, 255, 255), (0, 0, 0)  # Стандартные цвета (white, black)
        avg_color = [0, 0, 0]
        for point in points:
            c = img.getpixel(point)
            # img.putpixel(point, (255, 0, 0))
            avg_color = [avg_color[0] + c[0], avg_color[1] + c[1], avg_color[2] + c[2]]
        avg_color = [avg_color[0] / len(points), avg_color[1] / len(points), avg_color[2] / len(points)]
        dist2b = sqrt((avg_color[0] - b[0]) ** 2 + (avg_color[1] - b[1]) ** 2 + (avg_color[2] - b[2]) ** 2) / 3
        dist2w = sqrt((avg_color[0] - w[0]) ** 2 + (avg_color[1] - w[1]) ** 2 + (avg_color[2] - w[2]) ** 2)
        return w if dist2w >= dist2b else b

    # Вычисляем положение и цвет Водяного знака (pos_mark, pos_tg, pos_rt, pos_hsh, color)
    img = Image.open(path).convert("RGB")
    img_w, img_h = img.size

    with Image.open(f'{os.path.dirname(__file__)}/asset/watermark255.png') as mark:
        relation_mark = mark.size[1] / mark.size[0]

    min_mark_w = 50
    mark_w = min(img_w, img_h) / 12
    if mark_w < min_mark_w:
        mark_w = min_mark_w
    mark_w, mark_h = int(mark_w), int(relation_mark * mark_w)
    dst = int(mark_w / 4)

    pos_mark = (dst, img_h - mark_h - dst)
    pos_tg = (mark_w + int(1.5 * dst), img_h - dst - mark_h)
    pos_rt = (mark_w + int(1.5 * dst), img_h - dst - int(.66 * mark_h))
    pos_hsh = (mark_w + int(1.5 * dst), img_h - dst - int(.33 * mark_h))

    color = choose_color(*[(x, y)
                           for x in range(pos_mark[0], pos_mark[0] + 3 * mark_w, 5)
                           for y in range(pos_mark[1], pos_mark[1] + mark_h, 5)])

    mark = Image.open(f'{os.path.dirname(__file__)}/asset/watermark{color[0]}.png')
    mark = mark.resize(size=(mark_w, mark_h))
    mark_w, mark_h = mark.size

    # Добавляем Водяной знак на фото (mark, text)
    img_cnv = ImageDraw.Draw(img)
    img_cnv.text(pos_tg,
                 f"@RatePhotosBot",
                 font=ImageFont.truetype(f'{os.path.dirname(__file__)}/asset/Noah ExtraBold.ttf', mark_h / 3),
                 fill=color)
    img_cnv.text(pos_rt,
                 f"Оценено на {rt} из 10",
                 font=ImageFont.truetype(f'{os.path.dirname(__file__)}/asset/Noah Regular.ttf', mark_h / 3),
                 fill=color)
    img_cnv.text(pos_hsh,
                 f"Хэш {hsh}",
                 font=ImageFont.truetype(f'{os.path.dirname(__file__)}/asset/Noah Light.ttf', mark_h / 3),
                 fill=color)
    img.paste(mark, pos_mark, mask=mark)
    # img.save(path)
    img.save(path)


# watermark("photos/T3.jpg", 3745, "e5a1a7e5a1a77")
