"""
class & function list:
    load_user(user_id)
    User

"""
from ..extentions import db, login_manager, avatarUser, coverUser
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from .team import Team

class Follow(db.Model):
    __tablename__ = 'follows'

    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """
    class structure:
        column:
            auth
            profile
            real info
            password
    """
    __tablename__ = 'users'

    def __repr__(self):
        return '<User %r>' % self.username

    #info:auth
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    last_seen = db.Column(db.DateTime)
    lock = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    #role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    #info:profile
    avatar = db.Column(db.String(128))
    cover = db.Column(db.String(128))
    gender = db.Column(db.String(8), default='不告诉你')
    birthday = db.Column(db.DateTime)
    about_me = db.Column(db.String(100))

    #info:real identity
    name = db.Column(db.String(64))
    id_number = db.Column(db.String(18))
    phone = db.Column(db.String(15))
    address = db.Column(db.String(64))

    # password
    @property
    def password(self):
        raise AttributeError('password属性不可访问')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #avatar & cover
    @property
    def avatar_url(self):
        filename = self.avatar if self.avatar else 'default.jpg'
        return avatarUser.url(filename)

    @property
    def cover_url(self):
        filename = self.cover if self.cover else 'default.jpg'
        return coverUser.url(filename)

    #--------------关注----------------------
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               cascade='all, delete-orphan', lazy='dynamic')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                cascade='all, delete-orphan', lazy='dynamic')

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        follow = self.followed.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    #各种relationship------------团队---------------------------------
    leader_teams = db.relationship('Team', backref='leader', lazy='dynamic', foreign_keys=[Team.leader_id])
    user_teams = db.relationship('TeamUser', backref=db.backref('user', lazy='joined'),
                                 lazy = 'dynamic', cascade='all, delete-orphan')
    @property
    def teams_joined(self):
        return [item.team for item in self.user_teams.order_by('timestamp desc').all()]

    @property
    def leader_count(self):
        return self.leader_teams.count()

    @property
    def joined_team_count(self):
        return self.user_teams.count()

    #辅助工具
    @staticmethod
    def get_user(id):
        if id == 0:
            return current_user
        else:
            return User.query.get_or_404(id)

    #---------------relationship-----------活动
    activities_followed = db.relationship('FollowActivity', backref=db.backref('user', lazy='joined'),
                                          lazy='dynamic', cascade='all, delete-orphan')
    joins_activity = db.relationship('JoinActivity', lazy='dynamic', backref=db.backref('user', lazy='joined'))

    questions_activity = db.relationship('ActivityQuestion', lazy='dynamic', backref=db.backref('user', lazy='joined'))

    supports = db.relationship('CrowdFunding', lazy='dynamic', backref=db.backref('user', lazy='joined'))

    #TODO 分页
    def activities_follow(self):
        return [follow.activity for follow in self.activities_followed.order_by('follow_activities.timestamp desc').all()]

    def activities_join(self):
        return [join.activity for join in self.joins_activity.order_by('join_activities.timestamp desc').all()]














