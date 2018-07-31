from . import team
from flask import redirect, flash, render_template, url_for, request, session, abort
from ..models.activity import (
    Activity,
    JoinActivity,
    ActivityContact,
    ActivityQuestion,
    CrowdFunding,
    ActivitySolution,
    RegistrationWay,
    Volunteer,
    registration_way,
    volunteer_type)
from ..models.team import Team
from ..models.outdoorType import OutdoorType
from ..models.user import User
from flask_login import login_required, current_user
from ..forms.activity import (
    CreateActivityForm,
    ActivityJoinForm,
    ActivityContactsForm,
    ActivityAskForm,
    CrownSloganForm,
    CrownSupportForm,
    ActivitySearchForm,
    ActivitySolutionForm,
    ActivityVolunteerJoinForm,
    ActivityTeamJoinForm)
from ..tools.string_tools import get_md5_filename_w_ext, trans_html
from ..tools.photo import cut
from ..extentions import coverPost, db
import datetime
from ..tools.permissions import only_team_admin, only_team_available, only_self, only_user_id


"""
编辑活动
"""


def fill_activity(activity, form, new=False, club=None):
    if new:
        activity.created_by = current_user.id
        activity.belong_to_team = club.id
    activity.name = form.name.data
    activity.start_date = form.start_date.data
    activity.end_date = form.end_date.data
    activity.days = (activity.end_date - activity.start_date).days
    activity.rally_site = form.rally_site.data
    activity.destination = form.destination.data
    activity.price = form.price.data
    activity.maximum = form.maximum.data
    activity.intensity_index = form.intensity_index.data
    activity.landscape_index = form.landscape_index.data
    activity.phone = form.phone.data
    activity.registration = sum(form.registration_way.data)  # 注册方式直接求和
    activity.types = [OutdoorType.query.get(item) for item in form.travel_type.data]
    activity.introduce = trans_html(form.introduce.data)
    cover = form.cover.data
    if cover:
        filename = get_md5_filename_w_ext(current_user.username, cover.filename)
        cut(cover, coverPost.path(filename))
        activity.cover = filename
    return activity


@team.route('/activity/add/<int:id>', methods=['GET', 'POST'])
@login_required
def create_activity(id):
    group = Team.query.get_or_404(id)
    only_team_available(group)
    only_team_admin(group, current_user)
    form = CreateActivityForm()
    if form.validate_on_submit():
        activity = Activity()
        activity = fill_activity(activity, form, True, group)
        db.session.add(activity)
        db.session.commit()
        flash('活动发布成功，您可以选择添加多个活动方案')
        return redirect(url_for('.activity_add_sln', id = activity.id))
    return render_template('activity_add.html', form=form)


@team.route('/activity/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_activity(id):
    activity = Activity.query.get_or_404(id)
    only_team_available(activity.team)
    only_team_admin(activity.team, current_user)
    form = CreateActivityForm()
    if request.method == 'GET':
        #填充数据
        form.name.data = activity.name
        form.start_date.data = activity.start_date
        form.end_date.data = activity.end_date
        form.rally_site.data = activity.rally_site
        form.destination.data = activity.destination
        form.price.data = activity.price
        form.maximum.data = activity.maximum
        form.intensity_index.data = activity.intensity_index
        form.landscape_index.data = activity.landscape_index
        form.phone.data = activity.phone
        form.introduce.data = activity.introduce
        form.registration_way.data = [way for way in registration_way if way & activity.registration] #位操作符
        form.travel_type.data = [t.id for t in activity.types]
    if form.validate_on_submit():
        activity = fill_activity(activity, form)
        db.session.add(activity)
        db.session.commit()
        flash('活动更新成功成功，您可以选择继续维护活动方案')
        return redirect(url_for('.activity_add_sln', id = activity.id))
    return render_template('activity_add.html', form=form)


@team.route('/activity/sln/<int:id>', methods=['GET', 'POST'])
@login_required
def activity_add_sln(id):
    activity = Activity.query.get_or_404(id)
    only_team_admin(activity.team, current_user)
    form = ActivitySolutionForm()
    if form.validate_on_submit():
        if form.sln_id.data:
            #更新
            sln = ActivitySolution.query.get_or_404(int(form.sln_id.data))
            sln.edit(form.name.data, form.detail.data)
        # 新建
        else:
            ActivitySolution.add_solution(activity, form.name.data, form.detail.data)
        return redirect(url_for('.activity_add_sln', id=id))
    return render_template('activity_add_solutions.html',
                           activity=activity,
                           solutions = activity.solutions,
                           form=form)


@team.route('/activity/sln/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_sln(id):
    sln = ActivitySolution.query.get_or_404(id)
    activity_id=sln.activity.id
    db.session.delete(sln)
    return redirect(url_for('.activity_add_sln', id=activity_id))


@team.route('/activity/delete/<int:id>')
@login_required
def delete_activity(id):
    activity = Activity.query.get_or_404(id)
    only_team_available(activity.team)
    only_team_admin(activity.team, current_user)
    db.session.delete(activity)
    flash('活动已删除')
    return redirect(url_for('.team_index', id=current_user.leader_team.id))

"""
活动页
"""


@team.route('/activity/<int:id>', methods=['GET', 'POST'])
def activity(id):
    activity = Activity.query.get_or_404(id)
    activity.view()
    form = ActivityAskForm()
    #handle ask
    solutions = activity.solutions if activity.solotion_count else None #这里如果直接不判断直接用activity.solotions，不是空，是查询对象
    if form.validate_on_submit():
        ask = form.ask.data
        ActivityQuestion.add_question(activity, ask)
        flash('提问成功，已通知队长，请等候回复')
        return redirect(url_for('team.activity', id=id))
    return render_template('activity.html', activity=activity, form=form, solutions=solutions)

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


"""
报名
"""


@team.route('/activity/join/<int:id>', methods=['GET', 'POST'])
@login_required
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


@team.route('/activity/join_next/<int:id>', methods=['GET', 'POST'])
@login_required
def activity_join_contact(id):
    count = int(request.args['count'])
    team_id = request.args.get('team_id', 0, type=int)
    #TODO 添加count 没有的逻辑  需要解决不能验证的问题 正则表达式
    activity = Activity.query.get_or_404(id)
    if activity.past:
        flash('活动已过期，不能报名')
        return redirect(url_for('.activity', id=activity.id))
    form = ActivityContactsForm(solutions=activity.solutions)
    if request.method == 'GET':#如果POST回传错误，也会执行继续添加联系人
        for i in range(count):
            form.contacts.append_entry()
    if form.validate_on_submit():
        contacts = form.contacts.data
        sln = form.solution.data
        comment = form.comment.data
        province = form.province.data
        join = activity.join_person(contacts, sln, comment, province, team_id)
        return redirect(url_for('team.activity_confirm', id=join.id))
    return render_template('activity_contact.html', form=form, count=range(count))


@team.route('/activity/join/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def activity_join_edit(id):
    join = JoinActivity.query.get_or_404(id)
    only_user_id(join.user_id)
    activity = join.activity
    if activity.past:
        flash('活动已结束，不能修改')
        return redirect(url_for('.activity', id=join.activity_id))
    form = ActivityContactsForm(solutions=activity.solutions)
    if request.method == 'GET':#如果POST回传错误，也会执行继续添加联系人
        for i in range(join.count):
            form.contacts.append_entry()
        form.solution.data = join.solution
        form.comment.data = join.comment
        form.province.data = join.province
        for i in range(len(join.contacts.all())):
            form.contacts[i].real_name.data=join.contacts[i].name
            form.contacts[i].identity.data = join.contacts[i].identity
            form.contacts[i].gender.data = join.contacts[i].gender
            form.contacts[i].age.data = join.contacts[i].age
            form.contacts[i].phone.data = join.contacts[i].phone
    if form.validate_on_submit():
        contacts = form.contacts.data
        sln = form.solution.data
        comment = form.comment.data
        province = form.province.data
        if activity.past:
            flash('活动已过期')
            return
        join = activity.join_person_edit(contacts, sln, comment, province, join)
        flash('修改成功')
        return redirect(url_for('team.activity_confirm', id=join.id))
    return render_template('activity_contact.html', form=form)


@team.route('/activity/join_confirm/<int:id>', methods=['GET', 'POST'])
@login_required
def activity_confirm(id):
    #订单详细信息
    join = JoinActivity.query.get_or_404(id)
    team = request.args.get('team', 0, type=int)
    """form = CrownSloganForm()#注释掉的众筹信息
    if form.validate_on_submit():
        join.crowd_funding_text = form.slogan.data
        db.session.add(join)
        return redirect(url_for('team.crowd_funding_index', id=join.id))"""
    return render_template('activity_confirm.html', join=join, team=team)


@team.route('/activity/join/cancel/<int:id>')
@login_required
def activity_cancel(id):
    join = JoinActivity.query.get_or_404(id)
    db.session.delete(join)
    flash('您已取消参与该活动')
    return redirect(url_for('index'))


@team.route('/activity/join/details/<int:id>')
@login_required
def activity_join_details(id):
    activity = Activity.query.get_or_404(id)
    if not (activity.team.is_admin(current_user) or current_user.is_admin):
        abort(403)
    details = Activity.get_registration_details(activity.id)
    return render_template('activity_registration_details.html', contacts=details)


@team.route('/activity/join/volunteer/<int:id>', methods=['GET', 'POST'])
@login_required
def activity_join_volunteer(id):
    activity = Activity.query.get_or_404(id)
    form = ActivityVolunteerJoinForm(activity.solutions.all())
    form.phone = current_user.phone
    if form.validate_on_submit():
        join = activity.join_volunteer(form)
        flash('报名成功')
        return redirect(url_for('.activity_confirm', id=join.id))
    return render_template('activity_join_volunteer.html', form=form)


@team.route('/activity/join/team/<int:id>', methods=['GET', 'POST'])
@login_required
def activity_join_team(id):
    activity = Activity.query.get_or_404(id)
    form = ActivityTeamJoinForm(activity.solutions.all())
    if form.validate_on_submit():
        join = activity.join_team(form)
        flash('团队报名成功')
        return redirect(url_for('.activity_confirm', id=join.id, team=1))
    return render_template('activity_join_team.html', form=form)


@team.route('/activity/team_join/<int:id>', methods=['GET','POST'])
def activity_index_team(id):
    team_id = request.args.get('team_id', 0, type=int)
    if not team_id:
        abort(404)
    activity = Activity.query.get_or_404(id)
    team = Team.query.get_or_404(team_id)
    team_content = activity.get_team_content(team.id)
    if request.method == 'POST':
        count = request.form['count']
        return redirect(url_for('.activity_join_contact', id=id, count=count, team_id=team_id))
    return render_template('activity_team_join.html',
                           activity=activity,
                           team=team,
                           team_content=team_content)


@team.route('/activities/team_join/<int:id>')
def activitys_team_join(id):
    team = Team.query.get_or_404(id)
    activities = team.get_activities_joined()
    return render_template('activities_team_join.html',
                           activities=activities,
                           team=team)

"""
暂时不用的众筹页面
"""

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


@team.route('/activites/search', methods=['GET', 'POST'])
def activities_search():
    form = ActivitySearchForm()
    page = request.args.get('page', 1, type=int)
    if request.method == 'POST':
        #每次POST，添加查询字符串，取回第一页
        session['activity-keyword'] = form.keyword.data
        session['activity-outdoor'] = form.outdoor.data
        session['activity-days'] = form.days.data
        session['activity-sort'] = form.sort.data
        page = 1
    pagination = Activity.get_activities_search(
        session.get('activity-keyword', ""),
        session.get('activity-outdoor', 'None'),
        session.get('activity-days', 'None'),
        session.get('activity-sort', 'None'),
        page
    )
    activities = pagination.items
    return render_template('activities_search.html',
                           form=form,
                           activities = activities,
                           pagination = pagination)


@team.route('/activites/search/home')
def activities_search_home():
    #需要重置session
    session['activity-keyword'] = ""
    session['activity-outdoor'] = 'None'
    session['activity-days'] = 'None'
    session['activity-sort'] = 'None'
    return redirect(url_for('.activities_search'))



@team.route('/activities/search/<int:id>')
def activities_search_with_outdoor(id):
    if OutdoorType.query.filter_by(id=id).count:
        session['activity-outdoor'] = str(id)
        #清空其他session
        session['activity-keyword'] = ""
        session['activity-days'] = 'None'
        session['activity-sort'] = 'None'
        return redirect(url_for('.activities_search'))
    else:
        flash('您选择的活动分类不存在')










