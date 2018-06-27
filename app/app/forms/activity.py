from flask_wtf import Form
from wtforms import StringField, TextAreaField, RadioField, SubmitField, ValidationError, SelectMultipleField,\
    FieldList, FormField
from wtforms.fields.html5 import DateField, IntegerField
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import Length, DataRequired, Email, Regexp, NumberRange
from ..extentions import coverPost
from ..models.outdoorType import OutdoorType
from datetime import datetime, date


class CreateActivityForm(Form):
    name = StringField('活动标题', render_kw={'placeholder': '填写活动标题（100字以内）'},
                        validators=[DataRequired('必填字段'), Length(1, 100)])
    cover = FileField('活动封面', validators=[FileAllowed(coverPost, '请上传图片格式')])
    travel_type = SelectMultipleField('活动类型', coerce=int, validators=[DataRequired('请至少选择一个活动类型')])
    start_date = DateField('活动开始日期', validators=[DataRequired('必填字段')])
    end_date = DateField('活动结束日期', validators=[DataRequired('必填字段')])  # 自动计算活动天数
    phone = StringField('咨询电话', validators=[Length(1, 15)])
    maximum = IntegerField('活动参与人数')  #TODO 不填为不限人数
    rally_site = StringField('活动集合地点', render_kw={'placeholder': '填写活动集合地点（20字以内）'},
                              validators=[DataRequired('必填字段'), Length(1, 20)])
    destination = StringField('活动目的地', render_kw={'placeholder': '填写活动目的地（20字以内）'},
                           validators=[DataRequired('必填字段'), Length(1, 20)])
    price = IntegerField('成人价格', render_kw={'placeholder': '填写活动价格（仅数字，不加单位）'})
    #TODO-------------指数选择改成star selector-----
    intensity_index = IntegerField('强度指数（请填写数字1-5）', default='5', render_kw={'min': '1', 'max': '5'},
                                   validators=[DataRequired('必填字段'), NumberRange(min=1, max=5, message='数字只能在1-5之间')])
    landscape_index = IntegerField('风景指数（请填写数字1-5）', default='5', render_kw={'min': '1', 'max': '5'},
                                   validators=[DataRequired('必填字段'), NumberRange(min=1, max=5, message='数字只能在1-5之间')])
    introduce = CKEditorField('活动介绍', validators=[DataRequired('必填字段')])
    submit = SubmitField('发布活动')

    def __init__(self, *args, **kwargs):
        super(CreateActivityForm, self).__init__(*args, **kwargs)
        self.travel_type.choices = [(item.id, item.name) for item in OutdoorType.show_list()]

    def validate_end_date(self, field):
        if field.data < self.start_date.data:
            raise ValidationError('活动结束日期必须晚于活动开始日期')

    def validate_start_date(self, field):
        if field.data < date.today():
            raise ValidationError('活动日期必须在今天之后')


class ContactForm(Form):
    name = StringField('真实姓名', [DataRequired('必填项'), Length(min=2, max=10)])
    identity = StringField('身份证号', [DataRequired('必填项'), Length(min=16, max=18)])


class ActivityJoinForm(Form):
    count = IntegerField('人数', default=1, validators=[DataRequired()])
    phone = StringField('联系电话', [DataRequired('必填项'), Length(min=7, max=18)])
    submit = SubmitField('添加出行人详细信息')


class ActivityContactsForm(Form):
    contacts = FieldList(FormField(ContactForm))
    submit = SubmitField('确认出行人信息')


class ActivityAskForm(Form):
    ask = TextAreaField('我有问题', [DataRequired('请填写您的提问'), Length(max=500, message='您的提问最大输入500字')])
    submit = SubmitField('提问')


class CrownSloganForm(Form):
    slogan = TextAreaField('众筹宣言', [DataRequired('请输入您的宣言'), Length(max=500, message='最大输入500字')],
                           render_kw={'placeholder': '您的众筹宣言仅限500字'})
    submit = SubmitField('发起众筹')


class CrownSupportForm(Form):
    money = IntegerField('支持金额', [DataRequired('请填写金额')])
    text = TextAreaField('支持感言', [DataRequired('请输入您的感言'), Length(max=500, message='最大输入500字')],
                           render_kw={'placeholder': '您的感言仅限500字'}, default='加油')
    submit = SubmitField('我要支持')
