from flask import Flask, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_uploads import UploadSet, IMAGES
from flask_ckeditor import CKEditor
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Separator, Subgroup, Link


bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
ckeditor = CKEditor()

nav = Nav()
@nav.navigation()
def top_nav():
    return Navbar('小猫游园',
                  View('主页', 'index'),
                  View('活动', 'team.activities_search_home'),
                  View('团队', 'team.teams_search_home'),
                  View('申请俱乐部', 'team.create_team'),
                  View('我的主页', 'user.profile_me'),
                  View('我的俱乐部', 'team.team_me')
                  )


#头像上传
avatarUser = UploadSet('avatarUser', IMAGES)
avatarTeam = UploadSet('avatarTeam', IMAGES)
coverUser = UploadSet('coverUser', IMAGES)
imgTeam = UploadSet('imgTeam', IMAGES)
coverPost = UploadSet('coverPost', IMAGES)
commonImage = UploadSet('commonImage', IMAGES)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = '您需要登陆访问该资源哦'


