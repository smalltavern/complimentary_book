from sqlalchemy import Boolean, Column, Integer, ForeignKey, String, desc, func
from sqlalchemy.orm import relationship

from app.models.base import BaseModel, db
from app.spider.yushu_book import YushuBook


class Wish(BaseModel):
    id = Column(Integer, primary_key=True)
    user = relationship('User')
    uid = Column(Integer, ForeignKey('user.id'))
    isbn = Column(String(15), nullable=False, comment='isbn')
    # book = relationship('Book')
    # bid = Column(Integer, ForeignKey('book.id'))
    launched = Column(Boolean, default=False, comment='是否已经获得')

    @property
    def book(self):
        yushu_book = YushuBook()
        yushu_book.search_by_isbn(self.isbn)
        return yushu_book.first

    @classmethod
    def get_my_wishes(cls, uid):
        return cls.query.filter_by(uid=uid, launched=False).order_by(desc(cls.create_time)).all()

    @classmethod
    def get_gift_counts(cls, isbn_list):
        from app.models.gift import Gift
        """
        获取每个 isbn 所对应的赠送者的数量
        :param isbn_list:
        :return:
        """
        count_list = db.session.query(Gift.isbn, func.count(Gift.id)).filter(
            Gift.isbn.in_(isbn_list),
            Gift.status == 1
        ).group_by(Gift.isbn).all()
        # 上面的代码等同于如下 SQL
        # SELECT isbn,count(id) FROM wish WHERE status = 1 and isbn in('9787806579060','9787101028584') GROUP by isbn;

        return [{'isbn': g[0], 'count': g[1]} for g in count_list]