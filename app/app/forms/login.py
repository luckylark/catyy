from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email,ValidationError, Length, Regexp, EqualTo
from ..models.user import User


class LoginForm(Form):
    email = StringField('邮箱：', validators=[DataRequired("没有填写邮箱"), Email('邮箱格式不正确')])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')


class RegisterForm(Form):
    email = StringField('邮箱', validators=[DataRequired('请填写邮箱'), Length(1, 64, '邮箱长度必须在64个字符内'),
                                          Email('请输入正确的邮箱格式，方便之后找回密码')])
    username = StringField('用户名', validators=[DataRequired('请填写用户名'), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired('请填写密码'), EqualTo('confirmPassword', message='密码不一致')])
    confirmPassword = PasswordField('再次输入密码', validators=[DataRequired('请确认密码')])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已注册')


class ChangePasswordForm(Form):
    oldPassword = PasswordField('旧密码', [DataRequired('请输入旧密码')])
    password = PasswordField('密码', validators=[DataRequired('请填写密码'), EqualTo('confirmPassword', message='密码不一致')])
    confirmPassword = PasswordField('再次输入密码', validators=[DataRequired('请确认密码')])
    submit = SubmitField('修改密码')

