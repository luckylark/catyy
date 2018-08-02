from . import admin
from flask_login import current_user, login_required
from ..forms.outdoor import CreateOutdoorTypeForm
from flask import flash, render_template, redirect, url_for, request, abort
from ..models.outdoorType import OutdoorType
from ..extentions import commonImage, db
from ..tools.string_tools import get_md5_filename
from ..decorators import admin_required
from ..models.team import Team
from ..models.demand import Demand


@admin.route('/index')
@admin_required
def index():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin_index.html')


@admin.route('/demands')
@admin_required
def demands():
    page = request.args.get('page', 1, type=int)
    pagination  = Demand.get_pager(page)
    return render_template('demands.html', pagination=pagination, demands=pagination.items)



