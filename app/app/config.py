import os
from os import path

class Config:
    #TODO 修改秘钥 or 从环境导入
    #配置：秘钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'support a default secret key'

    #配置：数据库
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    #SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass

    #avatar:target directery
    UPLOADED_AVATARUSER_DEST = path.join(path.dirname(__file__), 'static', 'images', 'avatar_user')
    UPLOADED_AVATARTEAM_DEST = path.join(path.dirname(__file__), 'static', 'images', 'avatar_team')
    # cover:target directery
    UPLOADED_COVERUSER_DEST = path.join(path.dirname(__file__), 'static', 'images', 'cover_user')
    UPLOADED_COVERTEAM_DEST = path.join(path.dirname(__file__), 'static', 'images', 'cover_team')
    UPLOADED_COVERPOST_DEST = path.join(path.dirname(__file__), 'static', 'images', 'cover_post')
    UPLOADED_COMMONIMAGE_DEST = path.join(path.dirname(__file__), 'static', 'images')
    CKEDITOR_FILE_UPLOADER = '/ckupload/'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:40710044@localhost/CatDevDB'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:40710044@localhost/CatProdDB'


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:40710044@localhost/CatTestDB'

config = {'development':DevelopmentConfig,'production':ProductionConfig,'testing':TestConfig,'default':DevelopmentConfig}
