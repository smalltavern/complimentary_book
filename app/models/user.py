from datetime import datetime, timedelta, timezone
from math import floor

import jwt
from flask import current_app
from sqlalchemy import Column, String, Boolean, Float, Integer

from .base import db, BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import Serializer
from flask_login import UserMixin

from .drift import Drift
from .gift import Gift
from .wish import Wish
from ..libs.enums import PendingStatus
from ..libs.helper import is_isbn_or_key
from ..spider.yushu_book import YushuBook


class User(UserMixin, BaseModel):
    id = Column(db.Integer, primary_key=True)
    nickname = Column(String(24), nullable=False)
    phone_number = Column(String(18), unique=True)
    email = Column(String(50), unique=True, nullable=False)
    _password = Column('password', String(256))
    confirmed = Column(Boolean, default=False, comment='')
    beans = Column(Float, default=0, comment='鱼豆')
    send_counter = Column(Integer, default=0, comment='')
    receive_counter = Column(Integer, default=0, comment='')
    wx_open_id = Column(String(50))
    wx_name = Column(String(32))

    @property
    def summary(self):
        return dict(
            nickname=self.nickname,
            beans=self.beans,
            email=self.email,
            send_receive=str(f'{self.send_counter}/{self.receive_counter}')
        )

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, pwd_raw):
        self._password = generate_password_hash(pwd_raw)

    def can_send_drift(self):
        """
        鱼豆必须足够（大于等于 1）
        每索取两本书，自己就必须送出一本书
        :return: boolean
        """
        if self.beans < 1:
            return False

        success_gift_count = Gift.query.filter_by(uid=self.id, launched=True).count()
        success_receive_count = Drift.query.filter_by(requester_id=self.id, pending=PendingStatus.success).count()
        if floor(success_receive_count / 2) <= floor(success_gift_count):
            return True
        else:
            return False

    def check_password(self, pwd_raw):
        return check_password_hash(self._password, pwd_raw)

    def can_save_to_list(self, isbn):
        # 不是 isbn
        if is_isbn_or_key(isbn) != 'isbn':
            return False

        # 系统中没有这本书
        yushu_book = YushuBook()
        yushu_book.search_by_isbn(isbn)
        if not YushuBook.first:
            return False

        # 不允许一个用户同时赠送多本相同的图书
        # 一个用户不能同时称为赠书者和索要者
        gifting = Gift.query.filter_by(uid=self.id, isbn=isbn, launched=False).first()
        wishing = Wish.query.filter_by(uid=self.id, isbn=isbn, launched=False).first()
        # 既不在赠送清单中，也不在心愿清单中才能添加
        if not gifting and not wishing:
            return True
        else:
            return False

    def token_generator(self, expiration=600):
        """
        生成重置密码需要的 token
        :param expiration:过期时间
        :return:
        """
        now = datetime.now(tz=timezone.utc)
        dic = {
            'exp': now + timedelta(seconds=expiration),
            'iat': now,  # 发行时间
            'iss': 'yushu',  # token签发者
            'data': {  # 内容，一般存放该用户id和开始时间
                'user_id': self.id
            }
        }
        return jwt.encode(payload=dic, key=current_app.config['SECRET_KEY'])  # 加密生成字符串

    @staticmethod
    def reset_password(token, pwd_raw):
        tk_decoder = jwt.decode(token, key=current_app.config['SECRET_KEY'], algorithms='HS256')
        if tk_decoder:
            user_id = tk_decoder['data']['user_id']
            if user_id:
                user = User.query.get(user_id)
                with db.auto_commit():
                    user.password = pwd_raw
                    db.session.add(user)
            return True
        else:
            return False