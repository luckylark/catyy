import os
import pymysql
pymysql.install_as_MySQLdb()

from app import create_app
from flask_script import Manager, Shell, Command
from flask_migrate import Migrate, MigrateCommand
from app.extentions import db
from app.models.user import User
from app.models.outdoorType import OutdoorType
from app.models.team import Team, TeamUser
from app.models.activity import Activity

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


@manager.shell
def make_shell_context():
    return dict(app=app, db=db, User=User, Team=Team, OutdoorType=OutdoorType, TeamUser=TeamUser, Activity=Activity)
manager.add_command('db', MigrateCommand)

@Command
def createdb():
    db.create_all()
    #create admin
    admin = User()
    admin.username = 'admin'
    admin.email = 'lucky_lark@163.com'
    admin.password = 'lihonglin92999'
    admin.is_admin = True
    db.session.add(admin)
    db.session.commit()
    #create fake user
    from app.forgery import gene_users
    gene_users()
    #添加户外分类

if __name__ == '__main__':
    manager.run()
