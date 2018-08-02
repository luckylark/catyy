from .extentions import (
    login_manager,
    db,
    moment,
    bootstrap,
    avatarTeam,
    avatarUser,
    coverPost,
    imgTeam,
    coverUser,
    commonImage,
    ckeditor,
    nav
)
from flask_uploads import patch_request_class, configure_uploads
from .config import config
from flask import Flask, redirect, url_for, render_template, flash
from flask_login import current_user


def create_app(config_name):
    """
    创建flask实例并配置
    初始化扩展
    注册蓝本
    :param config_name:
    :return: flask
    """
    #create instance
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    #initial extention with flask instance
    db.init_app(app)
    moment.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    ckeditor.init_app(app)
    nav.init_app(app)
    #image upload config
    configure_uploads(app, (avatarUser, avatarTeam, coverPost, imgTeam, coverUser, commonImage))
    patch_request_class(app, 5*1024*1024)

    #register blueprint
    from .auth import auth
    app.register_blueprint(auth)
    from .user import user
    app.register_blueprint(user)
    from .admin import admin
    app.register_blueprint(admin)
    from .team import team
    app.register_blueprint(team)

    @app.context_processor
    def inject_vars():
        from .models.activity import registration_way, volunteer_type, RegistrationWay
        from .models.tools import province
        return dict(RegistrationWay=registration_way, Province=province, VolunteerType=volunteer_type,Registration_Way=RegistrationWay)

    #add main router
    @app.route('/')
    def index():
        from .models.activity import Activity
        from .models.outdoorType import OutdoorType
        carousel_items = Activity.query.order_by(Activity.timestamp.desc()).limit(5).all()
        collection = OutdoorType.show_list()
        activities = Activity.get_activities_latest()
        from .models.team import Team
        teams = Team.query.limit(20).all()
        return render_template('home.html',
                               carousel_items = carousel_items,
                               collection=collection,
                               activities=activities,
                               teams=teams)

    @app.route('/invest', methods=['GET', 'POST'])
    def invest():
        from .models.demand import Demand
        from .forms.demand import DemandForm
        form = DemandForm()
        if form.validate_on_submit():
            demand = Demand(company=form.company.data,
                            contact = form.contact.data,
                            phone = form.phone.data,
                            image = form.image.data,
                            brand = form.brand.data,
                            product = form.product.data,
                            market = form.market.data,
                            other = form.other.data)
            if current_user.is_authenticated:
                demand.user_id = current_user.id
            db.session.add(demand)
            flash('您已经提交了您的需求，稍后会与您联系')
            return redirect(url_for('invest'))
        return render_template('invest.html', form=form)

    # -----------------ckeditor图片上传-----------

    @app.route('/ckupload/', methods=['POST'])
    def ckupload():
        from flask import request, make_response
        from .tools.string_tools import get_rnd_filename_w_ext
        import os
        error = ''
        url = ''
        callback = request.args.get("CKEditorFuncNum")
        if request.method == 'POST' and 'upload' in request.files:
            fileobj = request.files['upload']
            rnd_name = get_rnd_filename_w_ext(fileobj.filename)
            filepath = os.path.join(app.static_folder,'images', 'upload', rnd_name)
            # 检查路径是否存在，不存在则创建
            dirname = os.path.dirname(filepath)
            if not os.path.exists(dirname):
                try:
                    os.makedirs(dirname)
                except:
                    error = 'ERROR_CREATE_DIR'
            elif not os.access(dirname, os.W_OK):
                error = 'ERROR_DIR_NOT_WRITEABLE'
            if not error:
                fileobj.save(filepath)
                url = url_for('static', filename='%s/%s' % ('images/upload/', rnd_name))
        else:
            error = 'post error'
        res = """<script type="text/javascript">
              window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
            </script>""" % (callback, url, error)
        response = make_response(res)
        response.headers["Content-Type"] = "text/html"
        return response

    #---------错误处理--------------
    @app.errorhandler(404)
    def page_not_fount(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    @app.errorhandler(403)
    def internal_server_error(e):
        return render_template('403.html'), 403

    return  app
