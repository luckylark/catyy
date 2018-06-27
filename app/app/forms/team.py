from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Length
from ..models.outdoorType import OutdoorType


class CreateTeamForm(Form):
    name = StringField('队名', [DataRequired('请填写队名')])
    description = TextAreaField('口号', [Length(max=100, message='请输入<100字的口号')], description='最多输入100字')
    image = FileField('头像')
    cover = FileField('封面')
    types = SelectMultipleField('团队类型', [DataRequired('请选择团队类型')], coerce=int)
    submit = SubmitField('创建团队')

    def __init__(self, *args, **kwargs):
        super(CreateTeamForm, self).__init__(*args, **kwargs)
        self.types.choices = [(t.id, t.name) for t in OutdoorType.show_list()]
