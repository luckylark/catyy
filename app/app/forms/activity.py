from flask_wtf import Form
from wtforms import StringField, TextAreaField, RadioField, SubmitField, ValidationError, SelectMultipleField,\
    FieldList, FormField, HiddenField, SelectField
from ..tools.field_widget import MultiCheckboxField
from wtforms.fields.html5 import DateField, IntegerField, EmailField
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import Length, DataRequired, Email, Regexp, NumberRange
from ..extentions import coverPost
from ..models.outdoorType import OutdoorType
from ..models.activity import registration_way, volunteer_type, Activity
from datetime import datetime, date
from ..models.tools import province


class CreateActivityForm(Form):
    name = StringField('活动标题', render_kw={'placeholder': '填写活动标题（100字以内）'},
                        validators=[DataRequired('必填字段'), Length(1, 100)])
    cover = FileField('活动封面', validators=[FileAllowed(coverPost, '请上传图片格式')])
    travel_type = MultiCheckboxField('使用了自定义字段的活动类型', coerce=int, validators=[DataRequired('请至少选择一个活动类型')])
    start_date = DateField('活动开始日期', validators=[DataRequired('必填字段')])
    end_date = DateField('活动结束日期', validators=[DataRequired('必填字段')])  # 自动计算活动天数
    phone = StringField('咨询电话', validators=[Length(0, 15)])
    maximum = IntegerField('活动参与人数')  #TODO 不填为不限人数
    rally_site = StringField('活动集合地点', render_kw={'placeholder': '填写活动集合地点（20字以内）'},
                              validators=[DataRequired('必填字段'), Length(1, 20)])
    destination = StringField('活动目的地', render_kw={'placeholder': '填写活动目的地（20字以内）'},
                           validators=[DataRequired('必填字段'), Length(1, 20)])
    price = IntegerField('活动价格', render_kw={'placeholder': '填写活动价格（仅数字，不加单位）'})
    #TODO-------------指数选择改成star selector-----
    intensity_index = IntegerField('强度指数（请填写数字1-5）', default='5', render_kw={'min': '1', 'max': '5'},
                                   validators=[DataRequired('必填字段'), NumberRange(min=1, max=5, message='数字只能在1-5之间')])
    landscape_index = IntegerField('风景指数（请填写数字1-5）', default='5', render_kw={'min': '1', 'max': '5'},
                                   validators=[DataRequired('必填字段'), NumberRange(min=1, max=5, message='数字只能在1-5之间')])
    introduce = TextAreaField('活动介绍', [DataRequired('必填字段')])
    registration_way = MultiCheckboxField('报名方式', [DataRequired('必填项')], coerce=int)
    submit = SubmitField('发布活动')

    def __init__(self,activity=None, *args, **kwargs):
        super(CreateActivityForm, self).__init__(*args, **kwargs)
        self.travel_type.choices = [(item.id, item.name) for item in OutdoorType.show_list()]
        self.registration_way.choices = [(k, registration_way[k]) for k in registration_way]
        self.activity = activity

    def validate_end_date(self, field):
        if field.data < self.start_date.data:
            raise ValidationError('活动结束日期必须晚于活动开始日期')

    def validate_start_date(self, field):
        if field.data < date.today():
            raise ValidationError('活动日期必须在今天之后')

    def validate_name(self, field):
        if self.activity and self.activity.name == field.data:
            return True
        if Activity.query.filter_by(name=field.data).count():
            raise ValidationError('您使用的活动名和站内其他活动重名啦！请修改一下活动名~')



class ActivitySolutionForm(Form):
    sln_id = HiddenField('id')
    name = StringField('活动方案名', render_kw={'placeholder': '填写活动方案名（20字以内）'},
                       validators=[DataRequired('必填字段'), Length(1, 20)])
    detail = TextAreaField('方案详情', render_kw={'placeholder': '填写方案详情（500字以内）', 'rows': 4},
                       validators=[DataRequired('必填字段'), Length(1, 500)])
    submit = SubmitField('提交活动方案')


class ActivitySearchForm(Form):
    keyword = StringField('搜索关键字')
    outdoor = RadioField('活动类型')
    days = RadioField('出行天数')
    #TODO 出行月份 价格筛选
    sort = RadioField('排序方式')
    submit = SubmitField('搜索活动')

    def __init__(self, *args, **kwargs):
        super(ActivitySearchForm, self).__init__(*args, **kwargs)
        #为单选钮赋默认值
        self.outdoor.choices = [(item.id, item.name) for item in OutdoorType.show_list()]
        days_source = [(1, '1天'), (3, '2-3天'), (7, '4-7天'), (15, '8-15天'), (16, '16天以上')]
        self.days.choices = days_source
        sort_source = [(0, '最新发布'), (1, '最多访问'), (2, '价格由低到高'), (3, '价格由高到低')]
        self.sort.choices = sort_source

"""
三类报名
"""


class ActivityJoinForm(Form):
    count = IntegerField('人数', default=1, validators=[DataRequired('必填项')])
    phone = StringField('联系电话', [DataRequired('必填项'), Length(min=7, max=18, message='格式不对')])
    submit = SubmitField('添加出行人详细信息')


class ContactForm(Form):
    real_name = StringField('真实姓名', [DataRequired('必填项'), Length(min=2, max=10, message='仅限10字以内')], render_kw={'class': 'form-control'})
    identity = StringField('身份证号', [DataRequired('必填项'), Length(min=15, max=18, message='身份证格式不对')], render_kw={'class': 'form-control'})
    phone = StringField('联系电话', validators=[DataRequired('必填项'), Length(1, 15, message='格式不对')], render_kw={'class': 'form-control'})
    gender = SelectField('性别', choices=[(0, '男'), (1, '女')], coerce=int, render_kw={'class': 'form-control'})
    age = IntegerField('年龄', [NumberRange(max=120, message='请输入正确的年龄')], render_kw={'class': 'form-control'})


class ActivityContactsForm(Form):
    solution = SelectField('活动方案', coerce=int, render_kw={'class': 'form-control'})
    province = SelectField('选择您所在的省份', coerce=int, choices=list(enumerate(province)), render_kw={'class': 'form-control'})
    comment = TextAreaField('备注（最多可以输入100字）', [Length(max=100, message='仅限100字以内')], render_kw={'class': 'form-control'})
    contacts = FieldList(FormField(ContactForm), render_kw={'class': 'form-control'})
    submit = SubmitField('确认出行人信息', render_kw={'class': 'btn btn-success'})

    def __init__(self, solutions, *args, ** kwargs):
        super(ActivityContactsForm, self).__init__(*args, **kwargs)
        if solutions:
            self.solution.choices = [(item.id, item.name) for item in solutions]
        else:
            self.solution.choices = [(0, '该活动没有多个活动方案')]


class ActivityVolunteerJoinForm(Form):
    volunteer = SelectField('志愿者类型', coerce=int)
    solution = SelectField('活动方案', coerce=int)
    province = SelectField('选择您所在的省份', coerce=int, choices=list(enumerate(province)))
    real_name = StringField('真实姓名', [DataRequired('必填项'), Length(min=2, max=10, message='仅限10字以内')])
    identity = StringField('身份证号', [DataRequired('必填项'), Length(min=15, max=18, message='身份证格式不对')])
    real_phone = StringField('联系电话', validators=[DataRequired('必填项'), Length(1, 15, message='格式不对')])
    gender = SelectField('性别', choices=[(0, '男'), (1, '女')], coerce=int)
    age = IntegerField('年龄', [NumberRange(max=120, message='请输入正确的年龄')])
    comment = TextAreaField('备注（最多可以输入100字）', [Length(max=100, message='仅限100字以内')],
                            render_kw={'class': 'form-control'})
    submit = SubmitField('报名活动')

    def __init__(self, solutions, *args, ** kwargs):
        super(ActivityVolunteerJoinForm, self).__init__(*args, **kwargs)
        if solutions:
            self.solution.choices = [(item.id, item.name) for item in solutions]
        else:
            self.solution.choices = [(0, '该活动没有多个活动方案')]
        self.volunteer.choices = [(item, volunteer_type[item]) for item in volunteer_type]


class ActivityTeamJoinForm(Form):
    real_phone = StringField('确认联系电话', validators=[DataRequired('必填项'), Length(1, 15, message='格式不对')])
    solution = SelectField('活动方案', coerce=int)
    team_price = IntegerField('团队报名的活动价格（包含路费等其他资费，价格可能和活动价格不一致）',[DataRequired('必填项')])
    team_content = TextAreaField('队长有话说（最多可以输入500字）',
                                 [Length(max=500, message='仅限500字以内')])
    province = SelectField('选择您所在的省份', coerce=int, choices=list(enumerate(province)))
    real_name = StringField('真实姓名', [DataRequired('必填项'), Length(min=2, max=10, message='仅限10字以内')])
    identity = StringField('身份证号', [DataRequired('必填项'), Length(min=15, max=18, message='身份证格式不对')])
    gender = SelectField('性别', choices=[(0, '男'), (1, '女')], coerce=int)
    age = IntegerField('年龄', [NumberRange(max=120, message='请输入正确的年龄')])
    comment = TextAreaField('备注（最多可以输入100字）', [Length(max=100, message='仅限100字以内')],
                            render_kw={'class': 'form-control'})
    submit = SubmitField('团队报名')

    def __init__(self, solutions, *args, ** kwargs):
        super(ActivityTeamJoinForm, self).__init__(*args, **kwargs)
        if solutions:
            self.solution.choices = [(item.id, item.name) for item in solutions]
        else:
            self.solution.choices = [(0, '该活动没有多个活动方案')]


class ActivityAskForm(Form):
    ask = TextAreaField('我有问题', [DataRequired('请填写您的提问'), Length(max=500, message='您的提问最大输入500字')])
    submit = SubmitField('提问')





"""
暂时不用的众筹
"""


class CrownSloganForm(Form):
    slogan = TextAreaField('众筹宣言', [DataRequired('请输入您的宣言'), Length(max=500, message='最大输入500字')],
                           render_kw={'placeholder': '您的众筹宣言仅限500字'})
    submit = SubmitField('发起众筹')


class CrownSupportForm(Form):
    money = IntegerField('支持金额', [DataRequired('请填写金额')])
    text = TextAreaField('支持感言', [DataRequired('请输入您的感言'), Length(max=500, message='最大输入500字')],
                           render_kw={'placeholder': '您的感言仅限500字'}, default='加油')
    submit = SubmitField('我要支持')

