from . import team
from flask_login import current_user, login_required
from ..forms.team import CreateTeamForm
from flask import flash, render_template, redirect, url_for, request
from ..models.outdoorType import OutdoorType
from ..models.team import Team
from ..models.user import User
from ..extentions import commonImage, db, avatarTeam, coverTeam
from ..tools.photo import resize
from ..tools.string_tools import get_md5_filename_w_ext


@login_required
@team.route('/create_team', methods=['GET', 'POST'])
def create_team():
    form = CreateTeamForm()
    if form.validate_on_submit():
        group = Team()
        group.name = form.name.data
        group.created_by = current_user.id
        group.leader_id = current_user.id
        group.description = form.description.data
        group.types = [OutdoorType.query.get(t) for t in form.types.data]
        image = form.image.data
        if image:
            f_name = get_md5_filename_w_ext(current_user.username, image.filename)
            resize(image, avatarTeam.path(f_name))
            group.avatar = f_name
        cover = form.cover.data
        #TODO cover save code
        db.session.add(group)
        db.session.commit()
        return redirect(url_for('.team_index', id=group.id))
    return render_template('create_team.html', form=form)


@team.route('/team/<int:id>')
def team_index(id):
    group = Team.query.get_or_404(id)
    return render_template('team.html', team = group)


@team.route('/select_outdoor')
def select_outdoor():
    collection = OutdoorType.show_list()
    return render_template('select_type.html', collection = collection)


@team.route('/list/<int:id>')
def team_list(id):
    t = OutdoorType.query.get_or_404(id)
    collection = t.teams
    return render_template('type_list.html', t = t, collection = collection)


@login_required
@team.route('/join/<int:id>')
def join(id):
    group = Team.query.get_or_404(id)
    group.join(current_user._get_current_object())
    flash('您已经是%s的队员啦' % group.name)
    return redirect(url_for('.team_index', id=group.id))


@team.route('/members/<int:id>')
def members(id):
    t = Team.query.get_or_404(id)
    return render_template('members.html', team=t)


@team.route('/my')
@team.route('/my/<int:id>')
def my_teams(id=0):
    user = User.get_user(id)
    teams = user.leader_teams
    return render_template('team_detail_list.html', teams=teams)


@team.route('/joined')
@team.route('/joined/<int:id>')
def joined_teams(id=0):
    user = User.get_user(id)
    teams = user.teams_joined
    return render_template('team_detail_list.html', teams=teams)



