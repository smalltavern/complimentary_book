from flask import Flask
from flask_login import LoginManager

from app.models.user import User
from app.web import web
from app.models.base import db
from flask_mail import Mail

login_manager = LoginManager()
mail = Mail()


def create_app():
    app = Flask(__name__)
    # 载入配置文件
    app.config.from_object('app.secure')
    app.config.from_object('app.setting')
    # 注册flask-sqlAlchemy
    db.init_app(app)
    # 注册 flask-login
    login_manager.init_app(app)
    login_manager.login_view = 'web.login'
    login_manager.login_message = '请先登录或注册'
    # db.create_all()
    with app.app_context():
        db.create_all()
    # 注册mail
    mail.init_app(app)
    # 注册蓝图
    app.register_blueprint(web)
    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))