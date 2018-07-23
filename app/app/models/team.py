"""
CLASS Team:

CLASS TEAM_USERS
"""
from ..extentions import db, avatarTeam, coverTeam
from datetime import datetime
from .outdoorType import team_types
from .activity import Activity


class Team(db.Model):
    __tablename__ = 'teams'

    def __repr__(self):
        return '<Team %r>' % self.name

    #property:basic
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    leader_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    #property:info
    description = db.Column(db.String(100))
    bulletin = db.Column(db.String(500))
    cover = db.Column(db.String(128))
    avatar = db.Column(db.String(128))

    # --------------------------------------------------image-----------------------------------
    @property
    def avatar_url(self):
        filename = self.avatar if self.avatar else 'default.jpg'
        return avatarTeam.url(filename=filename)

    @property
    def cover_url(self):
        filename = self.cover if self.cover else 'default.jpg'
        return coverTeam.url(filename=filename)

    #property:type
    types = db.relationship('OutdoorType', secondary=team_types, backref=db.backref('teams', lazy='dynamic'))

    #-------------------------------members-----------------------------------------------
    team_members = db.relationship('TeamUser', backref=db.backref('team', lazy='joined'),
                              lazy='dynamic', cascade='all, delete-orphan')
    @property
    def members(self):
        return [item.user for item in self.team_members]

    @property
    def member_count(self):
        return self.team_members.count()

    def get_top_members(self, count=5):
        #TODO 排序
        return [item.user for item in self.team_members.limit(count).all()]

    def join(self, user):
        relation = TeamUser(team=self, user=user)
        db.session.add(relation)

    def is_member(self, user):
        return self.team_members.filter_by(user_id=user.id).count()

    def is_leader(self, user):
        return user.id == self.created_by

    #query for show
    #---------------------------活动-------------------------------------
    activities = db.relationship('Activity', lazy='dynamic', backref= db.backref('team', lazy='joined'))

    @property
    def activity_count(self):
        return self.activities.count()

    def get_top_activities(self, top=5):
        return self.activities.order_by(Activity.timestamp.desc()).limit(top).all()




class TeamUser(db.Model):
    __tablename__ = 'team_users'
    def __repr__(self):
        return '<TeamUser %r>' % self.team_id

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())



