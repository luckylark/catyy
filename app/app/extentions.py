from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES
from flask_ckeditor import CKEditor
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Separator, Subgroup


bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
ckeditor = CKEditor()

nav = Nav()
@nav.navigation()
def top_nav():
    return Navbar('小猫游园',
                  Subgroup('出行',
                           View('活动', 'index'),
                           View('俱乐部', 'index'),
                           View('景区', 'index'),
                           View('约伴', 'index'),
                           View('攻略', 'index'),
                           View('地接', 'index')),
                  View('社区', 'index'),
                  View('商城', 'index'),
                  View('住宿', 'index'),
                  View('保险', 'index')
                  )

#头像上传
avatarUser = UploadSet('avatarUser', IMAGES)
avatarTeam = UploadSet('avatarTeam', IMAGES)
coverUser = UploadSet('coverUser', IMAGES)
coverTeam = UploadSet('coverTeam', IMAGES)
coverPost = UploadSet('coverPost', IMAGES)
commonImage = UploadSet('commonImage', IMAGES)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = '您需要登陆访问该资源哦'
