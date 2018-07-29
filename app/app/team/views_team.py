from . import team
from flask_login import current_user, login_required
from ..forms.team import CreateTeamForm, ModifyTeamForm, TeamSearchForm
from flask import flash, render_template, redirect, url_for, request, session
from ..models.outdoorType import OutdoorType
from ..models.team import Team
from ..models.user import User
from ..extentions import commonImage, db, avatarTeam, imgTeam
from ..tools.photo import resize
from ..tools.string_tools import get_md5_filename_w_ext, get_filename_w_ext
from ..decorators import admin_required


"""
创建和修改团队
"""
@login_required
@team.route('/create_team', methods=['GET', 'POST'])
def create_team():
    #每个用户只能创建一个俱乐部
    if current_user.leader_team:
        flash('您已经创建了俱乐部，每个用户只能创建一个俱乐部，您不能再创建了哦')
        return redirect(url_for('index'))
    form = CreateTeamForm()
    if form.validate_on_submit():
        club = Team()
        assign_club(club, form)
        db.session.add(club)
        #将队长列入管理员和会员
        club.join(current_user, is_admin=True)
        db.session.add(current_user)
        db.session.commit()
        flash('创建团队成功，请等待审核')
        return redirect(url_for('.team_index', id=club.id))
    return render_template('create_team.html', form=form)


@login_required
@team.route('/modify_team/<int:id>', methods=['GET', 'POST'])
def modify_team(id):
    club = Team.query.get_or_404(id)
    if club.approved:
        flash('您的俱乐部已经审批通过，不能再修改申请信息')
        return redirect(url_for('index'))
    form = ModifyTeamForm(club)
    if request.method == 'GET':
        form.name.data = club.name
        form.description.data = club.description
        form.types.data = [t.id for t in club.types]
        form.classify.data = club.classify
        form.phone_show.data = club.phone_show
        form.phone.data = club.phone
    if form.validate_on_submit():
        assign_club(club, form)
        db.session.add(club)
        db.session.commit()
        #将队长作为管理员加入
        club.join(current_user, is_admin=True)
        flash('修改申请信息成功，请等待重新审核')
        return redirect(url_for('.team_index', id=club.id))
    return render_template('create_team.html', form=form)


def assign_club(club, form):
    club.name = form.name.data
    club.created_by = current_user.id
    club.leader_id = current_user.id
    club.description = form.description.data
    club.types = [OutdoorType.query.get(t) for t in form.types.data]
    club.classify = form.classify.data
    club.phone = form.phone.data
    club.phone_show = form.phone_show.data
    image = form.image.data
    if image:
        f_name = get_md5_filename_w_ext(current_user.username, image.filename)
        resize(image, avatarTeam.path(f_name))
        club.avatar = f_name
    # TODO cover save code
    document_image = form.document.data
    if document_image:
        d_name = get_filename_w_ext(club.name, document_image.filename)
        resize(document_image, imgTeam.path(d_name), 1000)
        club.document = d_name
    return club


"""
团队首页
"""
@team.route('/team/<int:id>')
def team_index(id):
    club = Team.query.get_or_404(id)
    return render_template('team.html', team = club)


@team.route('/team/me')
@login_required
def team_me():
    if current_user.leader_team:
        return redirect(url_for('.team_index', id=current_user.leader_team.id))
    flash('您还没有创建团队，您可以先申请一个团队')
    return redirect(url_for('.create_team'))

"""
团队列表
"""
@team.route('/search', methods=['GET', 'POST'])
def teams_search():
    form = TeamSearchForm()
    page = request.args.get('page', 1, type=int)
    if request.method == 'POST':
        # 每次POST，添加查询字符串，取回第一页
        session['team-keyword'] = form.keyword.data
        session['team-outdoor'] = form.outdoor.data
        session['team-classify'] = form.classify.data
        session['team-sort'] = form.sort.data
        page = 1
    pagination = Team.get_teams_search(
        session.get('team-keyword', ""),
        session.get('team-outdoor', 'None'),
        session.get('team-classify', 'None'),
        session.get('team-sort', 'None'),
        page
    )
    teams = pagination.items
    return render_template('teams_search.html',
                           form=form,
                           teams=teams,
                           pagination=pagination)


@team.route('/team/search/home')
def teams_search_home():
    #需要重置session
    session['team-keyword'] = ""
    session['team-outdoor'] = 'None'
    session['team-classify'] = 'None'
    session['team-sort'] = 'None'
    return redirect(url_for('.teams_search'))


@team.route('/select_outdoor')
def select_outdoor():
    collection = OutdoorType.show_list()
    return render_template('select_type.html', collection = collection)


@team.route('/list/<int:id>')
def team_list(id):
    t = OutdoorType.query.get_or_404(id)
    collection = t.teams
    return render_template('type_list.html', t = t, collection = collection)




"""
加入+会员
"""
@login_required
@team.route('/join/<int:id>')
def join(id):
    club = Team.query.get_or_404(id)
    club.join(current_user._get_current_object())
    flash('您已经是%s的队员啦' % club.name)
    return redirect(url_for('.team_index', id=club.id))


@team.route('/members/<int:id>')
def members(id):
    club = Team.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination, members = club.members(page=page)
    return render_template('members.html',
                           team=club,
                           members=members,
                           pagination=pagination)






