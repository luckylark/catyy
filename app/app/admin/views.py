from . import admin
from flask_login import current_user, login_required
from ..forms.outdoor import CreateOutdoorTypeForm
from flask import flash, render_template, redirect, url_for, request, abort
from ..models.outdoorType import OutdoorType
from ..extentions import commonImage, db
from ..tools.string_tools import get_md5_filename
from ..decorators import admin_required


@login_required
@admin.route('/index')
@admin_required
def index():
    # TODO 装饰器
    if not current_user.is_admin:
        abort(403)
    return render_template('admin_index.html')



