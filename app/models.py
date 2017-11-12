from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from sqlalchemy import or_
import hashlib
from markdown import markdown
import bleach
from flask import current_app, request, abort
from . import db, login_manage


class Permission:  # 权限常量,由自己定义和设计
    FOLLOW = 0X01  # 关注
    COMMENT = 0X02  # 评论
    WRITE_ARTICLES = 0X04  # 发布文章
    ADMIN = 0X08  # 内容协管员
    SUPER_ADMIN = 0X80  # 超级管理员


class Role(db.Model):  # 相当于django中的用户组
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True, index=True)  # 用户组的名字
    default = db.Column(db.Boolean, default=False, index=True)  # 普通用户的role.default默认为False
    permissions = db.Column(db.Integer)  # 存储用户组的权限总值

    users = db.relationship('User', backref='role', lazy='dynamic')  # 用户组与用户的一对多

    @staticmethod
    def insert_roles():
        roles = {
            '用户': (Permission.FOLLOW |
                   Permission.COMMENT |
                   Permission.WRITE_ARTICLES, True),
            '管理员': (Permission.FOLLOW |
                    Permission.COMMENT |
                    Permission.WRITE_ARTICLES |
                    Permission.ADMIN, False),
            '超级管理员': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions, role.default = roles[r]  # 通过r这个键取值
            # role.permissions = roles[r][0]
            # role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()
        # insert_roles() 函数并不直接创建新角色对象，而是通过角色名查找现有的角色，然后再进行更新。
        # 只有当数据库中没有某个角色名时才会创建新角色对象。
        # 如果以后更新了角色列表，就可以执行更新操作了。要想添加新角色，或者修改角色的权限，
        # 修改roles 数组，再运行函数即可


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))  # 密码hash值

    avatar = db.Column(db.String(64), nullable=True)  # 存储的是七牛的头像url
    real_name = db.Column(db.String(64), nullable=True)
    location = db.Column(db.String(64), nullable=True)
    about_me = db.Column(db.Text, nullable=True)

    ban_bool = db.Column(db.Boolean, default=True)  # 为False时禁用,不推荐用is_active字段完成这种操作

    member_since = db.Column(db.DateTime, default=datetime.utcnow)  # 注册时间
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)  # 最后访问时间

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # django会默认实现外键的反向关联

    boards = db.relationship('Board', backref='author', lazy='dynamic')  # 超级管理员与模块的一对多
    posts = db.relationship('Post', backref='author', lazy='dynamic')  # 用户与文章的一对多
    comments = db.relationship('Comment', backref='author', lazy='dynamic')  # 用户与评论的一对多
    stars = db.relationship('PostStar', backref='author', lazy='dynamic')  # 用户与点赞的一对多

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def show_permission(self):  # 返回权限的说明
        if self.role.name == '用户':
            return '关注用户 | 评论 | 发表文章'
        if self.role.name == '管理员':
            return '关注用户 | 评论 | 发表文章 | 管理评论'
        if self.role.name == '超级管理员':
            return '你是这个site的超级管理员(拥有至高权力)'

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:  # 先给管理员权限
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:  # 默认用户权限为default=True的权限组合
                self.role = Role.query.filter_by(default=True).first()

    def can(self, permissions):  # 对用户的权限进行验证,用于模板中判断登陆用户的权限
        return self.role is not None and (self.role.permissions & permissions) == permissions
        # 权限位与操作 (0x07&0x05)==0x05 True

    def is_super(self):  # 模板中超级管理员权限验证
        return self.can(Permission.SUPER_ADMIN)

    @staticmethod
    def authenticated(username_or_email, password):  # 效仿django,用于处理用户登录验证的函数
        user = db.session.query(User).filter(
            or_(User.email == username_or_email, User.username == username_or_email)).first()
        # 支持使用邮箱或者用户名登陆
        if user is not None and user.verify_password(password):
            if user.ban_bool is False:
                abort(403)  # 在认证方法中,就针对user被禁用的话,abort(403)
            return user
        return False

    @property
    def password(self):
        raise AttributeError('密码不可读')

    @password.setter
    def password(self, password):  # 生成密码hash
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):  # 验证密码
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'用户名:{self.username}'


class AnonymousUser(AnonymousUserMixin):  # 出于一致性,不用检测用户是否登陆,对游客也可以权限检测方法
    def can(self, permissions):
        return False

    def is_super(self):
        return False

login_manage.anonymous_user = AnonymousUser


@login_manage.user_loader
def load_user(user_id):  # login_manage的回调函数
    return User.query.get(int(user_id))


class Board(db.Model):  # 板块/分类的模型
    __tablename__ = 'boards'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 处在一对多中的多侧,引用外键
    posts = db.relationship('Post', backref='board', lazy='dynamic')

    def __repr__(self):
        return f'板块名是:{self.real_name},创建者是{self.author.username}'


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_remove = db.Column(db.Boolean, default=False)  # 隐藏评论,而不是物理上的删除

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))  # 引用文章的外键，属于哪一篇文章
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 引用用户的外键

    origin_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    parent_comment = db.relationship('Comment', backref='reply_set', remote_side=id)  # 回复的集合


class Post(db.Model):  # 文章
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), nullable=False)  # 标题不能为空
    content = db.Column(db.Text, nullable=False)  # 正文不能为空
    create_time = db.Column(db.DateTime, default=datetime.utcnow)  # 发布时间
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 修改时间
    read_count = db.Column(db.Integer, default=0)  # 点击次数
    is_remove = db.Column(db.Boolean, default=False)  # 隐藏文章,而不是物理上的删除
    high_light = db.Column(db.Boolean, default=False)  # 加精

    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'))  # 引用文章模块的外键
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 引用用户的外键

    comments = db.relationship('Comment', backref='post', lazy='dynamic')  # 文章与评论一对多
    stars = db.relationship('PostStar', backref='post', lazy='dynamic')  # 文章与点赞一对多

    def __repr__(self):
        return f'作者是{self.author.username}'


class PostStar(db.Model):
    __tablename__ = 'post_stars'  # 文章的点赞
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow())  # 点赞时间

    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 引用用户的外键
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))  # 引用文章的外键，属于哪一篇文章

