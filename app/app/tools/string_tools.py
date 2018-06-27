from pypinyin import lazy_pinyin
from werkzeug.utils import secure_filename
import hashlib
import time
import bleach


def get_md5_filename(name):
    return hashlib.md5((name + str(time.time())).encode('utf8')).hexdigest()[:15]


def get_md5_filename_w_ext(name, file):
    return get_md5_filename(name) + '.' + file.split('.')[1]


def trans_html(text, allow_tags=['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol',
                                 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'h4', 'p', 'span', 'table', 'thead',
                                 'tbody', 'td', 'tr']):
    return bleach.linkify(
        bleach.clean(text=text, tags=allow_tags, strip=True)
    )
