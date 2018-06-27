"""
CLASS Activity

"""
from ..extentions import db
from datetime import datetime
from .outdoorType import activity_types
from ..extentions import coverPost
from flask_login import current_user


class Activity(db.Model):
    """
    id
    标题/创建时间/归属团队/封面/
    开始日期/结束日期/天数
    集合地点/目的地
    联系电话
    最多参与人数/活动实际参与人数
    价钱/儿童价
    强度指数/风景指数
    行程安排
    浏览次数
    """
    __tablename__ = 'activities'

    def __repr__(self):
        return '<Activity : %r>' % self.name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, index=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    belong_to_team = db.Column(db.Integer, db.ForeignKey('teams.id'))
    cover = db.Column(db.String(128))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    days = db.Column(db.SmallInteger)
    rally_site = db.Column(db.String(20))
    destination = db.Column(db.String(20))
    phone = db.Column(db.String(15))
    maximum = db.Column(db.SmallInteger)
    members = db.Column(db.SmallInteger, default=0)
    price = db.Column(db.SmallInteger, nullable=False)
    child_price = db.Column(db.SmallInteger)
    intensity_index = db.Column(db.SmallInteger, nullable=False)
    landscape_index = db.Column(db.SmallInteger, nullable=False)
    introduce = db.Column(db.Text, nullable=False)
    view_count = db.Column(db.Integer, default=0)

    @property
    def cover_url(self):
        filename = self.cover or 'default.jpg'
        return coverPost.url(filename)

    @property
    def past(self):
        return self.start_date < datetime.now()

#--------------------------活动类型---------------------------
    types = db.relationship('OutdoorType', secondary=activity_types, backref=db.backref('activities', lazy='dynamic'))

    def view(self):
        self.view_count += 1
        db.session.add(self)

    #-----------------关注收藏-----------------
    followers = db.relationship('FollowActivity', lazy='dynamic', backref=db.backref('activity', lazy='joined'),
                                cascade='all, delete-orphan')

    @property
    def follow_count(self):
        return self.followers.count()

    #TODO 分页排序
    @property
    def follow_members(self):
        return [follow.user for follow in self.followers.order_by(FollowActivity.timestamp.desc()).all()]

    def is_following(self, user):
        return self.followers.filter_by(user_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            follow = FollowActivity(user_id=user.id, activity_id=self.id)
            db.session.add(follow)

    def unfollow(self, user):
        follow = self.followers.filter_by(user_id=user.id).first()
        if follow:
            db.session.delete(follow)

    #---------------报名----------
    joins = db.relationship('JoinActivity', lazy='dynamic', backref=db.backref('activity', lazy='joined'))

    def joined(self, user):
        return self.joins.filter_by(user_id=user.id).count == 1

    @property
    def users_joined(self):
        return [join.user for join in self.joins.filter_by(state=1).all()] #仅筛选付费用户

    #------------------咨询-----------------
    counsel = db.relationship('ActivityQuestion', lazy='dynamic', backref=db.backref('activity', lazy='joined'))

    @property
    def counsel_reverse(self):
        return self.counsel.order_by('activity_questions.timestamp desc').all()
    #TODO  分页


class JoinActivity(db.Model):
    __tablename__ = 'join_activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    count = db.Column(db.Integer, nullable=False) #订单几人
    price = db.Column(db.Integer) #订单总价钱
    state = db.Column(db.Boolean, default=False) #0-未付款 1-已付款
    payment = db.Column(db.Boolean, default=False) #F自付 T-众筹
    crowd_funding_amount = db.Column(db.Integer, default=0) #众筹金额
    crowd_funding_number = db.Column(db.Integer, default=0)  # 众筹人数
    crowd_funding_text = db.Column(db.String(500)) #众筹宣言
    contacts = db.relationship('ActivityContact', lazy='dynamic', backref=db.backref('join', lazy='joined'))
    supports = db.relationship('CrowdFunding', lazy='dynamic', backref=db.backref('join', lazy='joined')) #queryd对象

    @property
    def support_count(self):
        return self.supports.count()

    @property
    def supports_by_money(self):
        return self.supports.order_by('crowd_funding_details.money desc').all()


class CrowdFunding(db.Model):
    __tablename__ = 'crowd_funding_details'

    #支付成功后添加数据库记录
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    join_id = db.Column(db.Integer, db.ForeignKey('join_activities.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    money = db.Column(db.Integer) #支持金额
    text = db.Column(db.String(500)) #支持宣言


class ActivityContact(db.Model):
    __tablename__ = 'activity_contacts'

    id = db.Column(db.Integer, primary_key=True)
    join_id = db.Column(db.Integer, db.ForeignKey('join_activities.id'))
    name = db.Column(db.String(10), nullable=False)
    identity = db.Column(db.String(18), nullable=False)


class FollowActivity(db.Model):
    __tablename__ = 'follow_activities'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())


class ActivityQuestion(db.Model):
    __tablename__ = 'activity_questions'

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question = db.Column(db.String(500), nullable=False)
    reply = db.Column(db.String(500))

    @staticmethod
    def add_question(activity, ask):
        db.session.add(ActivityQuestion(activity_id=activity.id, question=ask, user_id=current_user.id))

    def reply( self, reply):
        set.reply = reply
        db.session.add(self)


class ReviewActivity(db.Model):
    __tablename__ = 'activity_reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    score = db.Column(db.SmallInteger)
    commend = db.Column(db.SmallInteger) #1-推荐 2-一般 3-不推荐
    body = db.Column(db.Text)
    reply = db.Column(db.Text)

    def reply_review(self, content):
        self.reply = content
        db.session.add(self)


#-------------fake-----to be deleted
def gene_join():
    from .user import User
    users = User.query.all()
    from random import randint
    activities = Activity.query.all()
    count = len(activities)
    for user in users:
        activity = activities[randint(0, count-1)]
        join = JoinActivity()
        join.user_id = user.id
        join.activity_id = activity.id
        join.count = 1
        join.state = 1
        db.session.add(join)
    db.session.commit()




