from sqlalchemy import Column, Integer, String

from app.models.base import db, BaseModel


class Book(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False, comment='书名')
    author = Column(String(30), default='未知')
    binding = Column(String(20), comment='装帧版本')
    publisher = Column(String(50), comment='出版社')
    price = Column(String(20), comment='价格')
    pages = Column(Integer, comment='总页数')
    Pubdate = Column(String(20), comment='出版日期')
    isbn = Column(String(15), nullable=False, unique=True, comment='isbn')
    summary = Column(String(1000), comment='简介')
    image = Column(String(50), comment='封面')