from PIL import Image, ImageDraw, ImageFont
from math import ceil
from pathlib import Path
import os

d = {
    5: ['image5.png'],
    4: ['image4.png'],
    3: ['image3.png'],
    2: ['image2.png'],
    1: ['image1.png']
}


def draw_tier_list(rates: dict, offset: int = 0):
    # цвета
    colors = {5: (255, 127, 127), 4: (255, 191, 127), 3: (255, 255, 127), 2: (191, 255, 127), 1: (127, 255, 127),
              0: (127, 255, 255)}
    tiers = {5: 'S', 4: 'A', 3: 'B', 2: 'C', 1: 'D', 0: 'E'}
    background_color = (26, 26, 23)
    text_color = (0, 0, 0)
    bold_font = ImageFont.truetype('Ubuntu-R.ttf', 90)
    sum = 0
    image_sum = 0
    for key, value in rates.items():
        image_sum += len(value)
        if len(value) > 20:
            sum += ceil(len(value) / 20)
        else:
            sum += 1
    # Размеры тирлиста и размер каждой картинки
    tier_width = 1000 // 3
    tier_height = 1000 // 3
    image_width = 750 // 3
    image_height = 1000 // 3
    width = image_width * 20 + tier_width
    height = sum * image_height
    max_size = 174 * 10 ** 6
    image_list = []
    if max_size / width < height:
        rates1, rates2 = {}, {}
        max_rows = max_size / width // image_height
        sum = 0
        for key, value in rates.items():
            if len(value) > 20:
                sum += ceil(len(value) / 20)
            else:
                sum += 1

            if sum < max_rows:
                rates1[key] = value
            else:
                rates2[key] = value
        image_list = draw_tier_list(rates1, offset + 1)
        image_list2 = draw_tier_list(rates2, image_list[3] + 1)
        return (image_list[0] + image_list2[0], image_list[1] + image_list2[1], image_list2[3])
    # Создание нового изображения тирлиста
    thumbnails = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(thumbnails)


    # Координаты, с которых начинаются размещения картинок в тирлисте
    x = 0
    y = 0
    prev = -1
    # Размещение картинок в тирлисте
    for rating, images_list in rates.items():
        x = 0
        cell_box = (x, y, x + tier_width, y + tier_height)

        draw.rectangle(cell_box, fill=colors[rating])
        if prev != -1:
            _, _, w, h = draw.textbbox((0, 0), tiers[rating + 1], font=bold_font)
            draw.text((x + (tier_width - w) // 2, y - tier_height * prev + (tier_height * prev - h) // 2),
                      tiers[rating + 1], font=bold_font,
                      fill=text_color)

        x += tier_width
        cnt = 0
        list_length = len(images_list)
        prev = 1
        for image_path in images_list:
            cnt += 1
            image = Image.open(image_path)
            width, height = image.size
            new_width = int((image_height / height) * width)
            resized_image = image.resize((new_width, image_height))
            if new_width < image_width:
                thumbnails.paste(resized_image, (x, y))
                x += new_width
            else:

                # Обрезаем изображение по краям
                left = (new_width - image_width) / 2
                top = (image_height - image_height) / 2
                right = left + image_width
                bottom = top + image_height
                cropped_image = resized_image.crop((left, top, right, bottom))
                thumbnails.paste(cropped_image, (x, y))
                x += image_width
            if cnt % 20 == 0 and cnt != list_length:
                prev += 1
                y += image_height
                x = 0
                cell_box = (x, y, x + tier_width, y + tier_height)
                draw.rectangle(cell_box, fill=colors[rating])
                x += tier_width
        y += image_height

    if prev != -1:
        x = 0
        _, _, w, h = draw.textbbox((0, 0), tiers[rating], font=bold_font)
        draw.text((x + (tier_width - w) // 2, y - tier_height * prev + (tier_height * prev - h) // 2), tiers[rating],
                  font=bold_font,
                  fill=text_color)

    # Сохранение тирлиста в файл
    offset = offset if offset != 0 else ''
    file_path = f'tier_list{offset}.png'
    thumbnails.save(file_path)

    max_file_size_for_telegram = 49
    required = max_file_size_for_telegram * 2 ** 20
    file_size = os.path.getsize(file_path)
    file_path_comp = f'tier_list_compressed{offset}.png'
    if file_size > required:
        ratio = required / file_size
        image = Image.open(file_path)
        new_width = int(image.width * ratio ** 0.6)
        new_height = int(image.height * ratio ** 0.6)
        resized_image = image.resize((new_width, new_height))
        resized_image.save(file_path_comp)
    else:
        image = Image.open(file_path).save(file_path_comp)
    return (image_sum, [file_path_comp], offset)


if __name__ == '__main__':
    print(draw_tier_list(d))
