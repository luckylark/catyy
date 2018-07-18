from .extentions import (
    login_manager,
    db,
    moment,
    bootstrap,
    avatarTeam,
    avatarUser,
    coverPost,
    coverTeam,
    coverUser,
    commonImage,
    ckeditor,
    nav
)
from flask_uploads import patch_request_class, configure_uploads
from .config import config
from flask import Flask, redirect, url_for, render_template


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
    configure_uploads(app, (avatarUser, avatarTeam, coverPost, coverTeam, coverUser, commonImage))
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

    #add main router
    @app.route('/')
    def index():
        from .models.activity import Activity
        carousel_items = Activity.query.order_by(Activity.timestamp.desc()).limit(5).all()
        return render_template('home.html', carousel_items = carousel_items)

    return  app
