from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES
from flask_ckeditor import CKEditor


bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
ckeditor = CKEditor()

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
