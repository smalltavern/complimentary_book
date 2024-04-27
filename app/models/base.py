from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy  # 将导入的类重命名
from flask_sqlalchemy.query import Query as SQLAlchemyQuery
from sqlalchemy import Column, SmallInteger, Integer
from contextlib import contextmanager
from datetime import datetime


# 继承 SQLAlchemy 并添加 auto_commit 方法，可以是调用更加简单
class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


class Query(SQLAlchemyQuery):
    def filter_by(self, **kwargs):
        if 'status' not in kwargs.keys():
            kwargs['status'] = 1
        return super(Query, self).filter_by(**kwargs)


db = SQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True
    create_time = Column('create_time', Integer)
    status = Column(SmallInteger, default=1, comment='删除状态：1-存在，0-已经删除')

    def __init__(self):
        self.create_time = int(datetime.now().timestamp())

    def set_attrs(self, attr_dict):
        for key, value in attr_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    @property
    def create_datetime(self):
        if self.create_time:
            return datetime.fromtimestamp(self.create_time)
        else:
            return None