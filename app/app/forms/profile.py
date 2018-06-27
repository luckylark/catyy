from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
from wtforms.validators import DataRequired
from ..tools.photo import resize


class PhotoForm(Form):
    avatar = FileField('选择图片：', [DataRequired('请选择图片')])
    submit = SubmitField('上传图片')
