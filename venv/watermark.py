from PIL import Image, ImageDraw, ImageFont


def watermark(path: str, rt: int, hsh: str):
    img, wm = Image.open(path), Image.open("asset/watermark.png")
    img_w, img_h = img.size

    sqr = min(img_w, img_h) / 12
    wm = wm.resize(size=(int(sqr), int(wm.size[1] / wm.size[0] * sqr)))

    wm_w, wm_h = wm.size
    dst = int(wm_w / 4)

    img_cnv = ImageDraw.Draw(img)
    img_cnv.text((wm_w + dst + dst/2, img_h - dst - wm_h),
                 f"@RatePhotosBot",
                 font=ImageFont.truetype('asset/Noah ExtraBold.ttf', wm_h/3),
                 fill=(255, 255, 255))
    img_cnv.text((wm_w + dst + dst/2, img_h - dst - 2 * wm_h/3),
                 f"Оценено на {rt} из 10",
                 font=ImageFont.truetype('asset/Noah Regular.ttf', wm_h/3),
                 fill=(255, 255, 255))
    img_cnv.text((wm_w + dst + dst/2, img_h - dst - wm_h/3),
                 f"Хэш {hsh}",
                 font=ImageFont.truetype('asset/Noah Light.ttf', wm_h/3),
                 fill=(255, 255, 255))
    img.paste(wm, (dst, img_h - wm_h - dst), mask=wm)

    img.save(path)
