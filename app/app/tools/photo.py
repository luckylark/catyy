from PIL import Image
import qrcode
from flask import current_app, send_from_directory, url_for
from .string_tools import get_rnd_filename_w_ext
import os

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


#主要用于剪裁团队个人头像，不管图片多大都固定高度200
def resize_fix_height(image, path, height=200):
    img = Image.open(image)
    original_w, original_h = img.size
    width = int(original_w*height/original_h)
    img = img.resize((width, height))
    img.save(path)


def resize_fix_width(image, path, width=200):
    img = Image.open(image)
    original_w, original_h = img.size
    height = int(original_h*width/original_w)
    img = img.resize((width, height))
    img.save(path)


def cut(image, path, scale=0.6):
    img = Image.open(image)
    w, h = img.size
    if h/w > scale:
        h = w * scale
        img = img.crop((0, 0, w, h))
    img.save(path)


def qrcode_img(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    base_path = os.path.join(current_app.static_folder, 'images', 'qrcode')
    filename = get_rnd_filename_w_ext('test.png')
    img.save(os.path.join(base_path, filename))
    return filename


def qrcode_url(filename):
    return url_for('static', filename='images/qrcode/' + filename)


def paste_qrcode(url, path):
    pass


