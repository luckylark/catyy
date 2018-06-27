"""
view list:
login()
logout()
"""
from . import auth
from ..forms.login import LoginForm
from flask import render_template, flash, redirect, request, url_for
from flask_login import login_user, logout_user, current_user, login_required
from ..models.user import User


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登陆
    :return:跳转or错误信息
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first_or_404()
        if user:
            if user.verify_password(form.password.data):
                if not user.lock:
                    login_user(user, remember=form.remember_me.data)
                    return redirect(request.args.get('next') or url_for('index'))
                else:
                    flash('您的账户已被锁定，请与管理员联系')
            else:
                flash('密码输入错误，请重试')
        else:
            flash('邮箱不存在，请注册')
    return render_template('login.html', form=form)


@login_required
@auth.route('/logout')
def logout():
    """
    用户注销
    :return:跳转到主页
    """
    logout_user()
    flash('您已退出登陆')
    return redirect(url_for('index'))
