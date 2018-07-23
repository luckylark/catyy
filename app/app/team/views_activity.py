from . import team
from flask import redirect, flash, render_template, url_for, request, session
from ..models.activity import Activity, JoinActivity, ActivityContact, ActivityQuestion, CrowdFunding
from ..models.team import Team
from ..models.outdoorType import OutdoorType
from ..models.user import User
from flask_login import login_required, current_user
from ..forms.activity import CreateActivityForm, ActivityJoinForm, ActivityContactsForm, ActivityAskForm,\
    CrownSloganForm, CrownSupportForm
from ..tools.string_tools import get_md5_filename_w_ext, trans_html
from ..tools.photo import cut
from ..extentions import coverPost, db
import datetime


#--------------活动本身-----------------------------------------------
@login_required
@team.route('/activity/add/<int:id>', methods=['GET', 'POST'])
def create_activity(id):
    group = Team.query.get_or_404(id)
    form = CreateActivityForm()
    if form.validate_on_submit():
        activity = Activity()
        activity.name = form.name.data
        activity.created_by = current_user.id
        activity.belong_to_team = id
        activity.types = [OutdoorType.query.get(item) for item in form.travel_type.data]
        activity.start_date = form.start_date.data
        activity.end_date = form.end_date.data
        activity.days = (activity.end_date - activity.start_date).days
        activity.rally_site = form.rally_site.data
        activity.destination = form.destination.data
        activity.price = form.price.data
        activity.max_members = form.maximum.data
        activity.intensity_index = form.intensity_index.data
        activity.landscape_index = form.landscape_index.data
        activity.phone = form.phone.data
        #TODO CKEDITOR
        activity.introduce = trans_html(form.introduce.data)
        cover = form.cover.data
        if cover:
            filename = get_md5_filename_w_ext(current_user.username, cover.filename)
            cut(cover, coverPost.path(filename))
            activity.cover = filename
        db.session.add(activity)
        db.session.commit()
        flash('活动发布成功')
        return redirect(url_for('.activity', id = activity.id))
    return render_template('activity_add.html', form=form)


@team.route('/activity/<int:id>', methods=['GET', 'POST'])
def activity(id):
    activity = Activity.query.get_or_404(id)
    activity.view()
    form = ActivityAskForm()
    #handle ask
    if form.validate_on_submit():
        ask = form.ask.data
        ActivityQuestion.add_question(activity, ask)
        flash('提问成功，已通知队长，请等候回复')
        return redirect(url_for('team.activity', id=id))
    return render_template('activity.html', activity=activity, form=form)


@team.route('/activity/edit/<int:id>')
def edit_activity(id):
    pass


@team.route('/activity/delete/<int:id>')
def delete_activity(id):
    pass


#---------------------关注------------------------------------------
@team.route('/activity/follow/<int:id>')
def follow(id):
    activity = Activity.query.get_or_404(id)
    activity.follow(current_user)
    flash('关注成功')
    return redirect(url_for('.activity', id=id))


#TODO 分页
@team.route('/activities/follow/')
@team.route('/activities/follow/<int:id>')
def activities_follow(id=0):
    user = User.get_user(id)
    activities = user.activities_follow()
    return render_template('activities_follow.html', activities = activities)


#---------------------------------报名------------------
@login_required
@team.route('/activity/join/<int:id>', methods=['GET', 'POST'])
def activity_join(id):
    form = ActivityJoinForm()
    if request.method == 'GET' and current_user.phone:
        session['phone'] = current_user.phone
        form.phone.data = current_user.phone
    if form.validate_on_submit():
        #处理联系电话
        if not current_user.phone or (session.get('phone') != form.phone.data):
            current_user.phone = form.phone.data
            db.session.add(current_user)
        return redirect(url_for('team.activity_join_contact', id=id, count=form.count.data))
    return render_template('activity_join.html', form=form)


@login_required
@team.route('/activity/join_next/<int:id>', methods=['GET', 'POST'])
def activity_join_contact(id):
    count = int(request.args['count'])
    #TODO 添加count 没有的逻辑  需要解决不能验证的问题 正则表达式
    form = ActivityContactsForm()
    if request.method == 'POST':
        contacts = form.contacts.data
        activity = Activity.query.get_or_404(id)
        if activity.past:
            flash('活动已过期')
            return
        if validate_contacts(contacts, count):
            join = JoinActivity()
            join.user_id = current_user.id
            join.activity_id = activity.id
            join.count = count
            join.price = activity.price * count
            join.state = False
            db.session.add(join)
            db.session.commit()
            #--contact--
            for contact in contacts:
                db.session.add(ActivityContact(join_id=join.id, name=contact['name'], identity=contact['identity']))
            return redirect(url_for('team.activity_confirm', id=join.id))
    return render_template('activity_contact.html', form=form, count=range(count))


#----辅助校验函数----
def validate_contacts(contacts, count):
    if count != len(contacts):
        flash('出行人人数不对')
        return False
    for contact in contacts:
        name = contact['name']
        identity = contact['identity']
        # ------validate-----
        if not name:
            flash('姓名不能为空')
            return False
        if not identity:
            flash('身份证号不能为空')
            return False
        if len(name) > 10:
            flash('姓名过长')
            return False
        if len(identity) > 18:
            flash('身份账号输入不正确')
            return False
    return True


@login_required
@team.route('/activity/join_confirm/<int:id>', methods=['GET', 'POST'])
def activity_confirm(id):
    #订单详细信息
    join = JoinActivity.query.get_or_404(id)
    form = CrownSloganForm()
    if form.validate_on_submit():
        join.crowd_funding_text = form.slogan.data
        db.session.add(join)
        return redirect(url_for('team.crowd_funding_index', id=join.id))
    return render_template('activity_confirm.html', join=join, form=form)


@team.route('/crowd_funding/index/<int:id>')
def crowd_funding_index(id):     #TODO 众筹分享页面
    join = JoinActivity.query.get_or_404(id)
    percentage = int(join.crowd_funding_amount / join.price * 100) if int(join.crowd_funding_amount / join.price) < 1 else 100
    return render_template('crowd_funding_index.html', join=join, percentage=percentage)


@login_required
@team.route('/crowd_funding/support/<int:id>', methods=['GET', 'POST'])
def crowd_funding_support(id):
    join = JoinActivity.query.get_or_404(id)
    form = CrownSupportForm()
    if form.validate_on_submit():
        #TODO 付款成功再添加数据记录
        support = CrowdFunding()
        support.user_id = current_user.id
        support.join = join
        support.text = form.text.data
        support.money = form.money.data
        support.join.crowd_funding_number += 1
        support.join.crowd_funding_amount += support.money
        db.session.add(support)
        flash('支持成功，谢谢您的支持')
        return redirect(url_for('team.crowd_funding_index', id=join.id))
    return render_template('crowd_funding_support.html', form=form, join=join)

'''
取得各种活动列表
'''

@team.route('/activities/team/<int:id>')
def activities_team(id):
    team = Team.query.get_or_404(id)
    activities = team.activities.order_by('activities.timestamp desc').all()
    return render_template('activities_team.html', activities=activities, team=team)


@team.route('/activities/outdoor/<int:id>')
def activities_outdoor(id):
    outdoor = OutdoorType.query.get_or_404(id)
    activities = outdoor.activities.order_by(Activity.timestamp.desc()).all()
    return render_template('activities_outdoor.html', activities=activities)










