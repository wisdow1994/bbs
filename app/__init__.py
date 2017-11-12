from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_admin import Admin
from flask_security import templates


from config import config
csrf = CSRFProtect()
admin = Admin()
# ajax提交post和get请求,少了这一个,是万万不行的
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manage = LoginManager()
login_manage.session_protection = 'basic'
login_manage.blueprint_login_views = {
    'cms': 'cms.login',
    'auth': 'auth.login',
    # 'front': 'front.login'
}
# 记录登陆页面的端点,一个蓝图对应一个login_view视图函数


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    admin.init_app(app)
    csrf.init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    login_manage.init_app(app)

    from .cms import cms as cms_blueprint
    from .auth import auth as auth_blueprint

    app.register_blueprint(cms_blueprint)
    # app.register_blueprint(auth_blueprint, url_perfix='/auth')
    app.register_blueprint(auth_blueprint)

    return app
