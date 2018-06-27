import os
import pymysql
pymysql.install_as_MySQLdb()

from app import create_app
from flask_script import Manager, Shell
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

if __name__ == '__main__':
    manager.run()
