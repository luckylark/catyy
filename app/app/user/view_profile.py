from . import user
from ..models.user import User
from flask import render_template, flash, redirect, request, url_for
from flask_login import login_required, current_user
from ..forms.profile import PhotoForm, EditProfileForm
import os
from ..extentions import avatarUser, db
from ..tools.photo import resize


@login_required
@user.route('/modify_avatar', methods=['GET', 'POST'])
def modify_avatar():
    """
    提交新头像：
        删除原头像
        resize新头像
        保存新头像(in file & database)
    :return:
    """
    form = PhotoForm()
    if form.validate_on_submit():
        if current_user.avatar:
            os.remove(avatarUser.path(filename=current_user.avatar))
        image = form.avatar.data
        imagename = str(current_user.id) + '.' + image.filename.rsplit('.')[1]
        imagepath = avatarUser.path(filename=imagename)
        resize(image, imagepath)
        current_user.avatar = imagename
        db.session.add(current_user)
        return redirect(url_for('.profile', id=current_user.id))
    return render_template('modify_avatar.html', form=form)


@user.route('/profile/<int:id>')
def profile(id):
    user = User.query.get_or_404(id)
    return render_template('profile.html', user = user)


@user.route('/profile/details/<int:id>')
def profile_details(id):
    user = User.query.get_or_404(id)
    return render_template('profile_details.html', user = user)


@login_required
@user.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()
    if request.method == 'GET':
        form.username.data = current_user.username
        form.gender.data = current_user.gender
        form.birthday.data = current_user.birthday
        form.about_me.data = current_user.about_me
        form.name.data = current_user.name
        form.phone.data = current_user.phone
        form.id_number.data = current_user.id_number
        form.address.data = current_user.address
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.gender = form.gender.data
        current_user.birthday = form.birthday.data
        current_user.about_me = form.about_me.data
        current_user.phone = form.phone.data
        current_user.name = form.name.data
        current_user.id_number = form.id_number.data
        current_user.address = form.address.data
        db.session.add(current_user)
        flash('个人资料编辑成功')
        return redirect(url_for('user.profile_details', id=current_user.id))
    return render_template('edit_profile.html', form=form)



