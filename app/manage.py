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
    types = [['南太行', '100', 'outdoor_type/nantaihang.gif'],
             ['户外登山', '90', 'outdoor_type/huwaidengshan.jpg'],
             ['攀岩', '80', 'outdoor_type/panyan.jpg'],
             ['骑行', '70', 'outdoor_type/qixing.jpg'],
             ['健步走', '60', 'outdoor_type/jianbuzou.jpg'],
             ['垂钓', '50', 'outdoor_type/chuidiao.jpg'],
             ['漂流', '40', 'outdoor_type/piaoliu.jpg'],
             ['跑步', '30', 'outdoor_type/paobu.jpg']
             ]
    for t in types:
        outdoor_type = OutdoorType()
        outdoor_type.name = t[0]
        outdoor_type.weight = t[1]
        outdoor_type.image = t[2]
        outdoor_type.created_by = admin.id
        db.session.add(outdoor_type)
        db.session.commit




if __name__ == '__main__':
    manager.run()
