"""
view list:
login()
logout()
"""
from . import auth
from ..forms.login import LoginForm, RegisterForm, ChangePasswordForm
from flask import render_template, flash, redirect, request, url_for
from flask_login import login_user, logout_user, current_user, login_required
from ..models.user import User
from .. import db


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


@auth.route('/logout')
@login_required
def logout():
    """
    用户注销
    :return:跳转到主页
    """
    logout_user()
    flash('您已退出登陆')
    return redirect(url_for('index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        user.follow(user)  # 关注自己
        db.session.add(user)
        flash('注册成功，您现在可以登陆了')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form= form)


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.add(current_user)
        flash('密码修改成功')
        return redirect(url_for('user.profile', id=current_user.id))
    return render_template('change_password.html', form=form)




