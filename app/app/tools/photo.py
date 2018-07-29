from PIL import Image


def resize(image, path, width=200):
    img = Image.open(image)
    original_w, original_h = img.size
    if max(original_h, original_w) > width:
        if original_w > original_h:
            w = width
            h = int(w * original_h / original_w)
        else:
            h = width
            w = int(h * original_w / original_h)
        img = img.resize((w, h))#这里注意！必须要赋值！！！不是在原图操作，是返回操作成功的图片
    img.save(path)


def cut(image, path, scale=0.6):
    img = Image.open(image)
    w, h = img.size
    if h/w > scale:
        h = w * scale
        img = img.crop((0, 0, w, h))
    img.save(path)



