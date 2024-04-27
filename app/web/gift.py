from flask import current_app, flash, render_template, url_for, redirect
from flask_login import login_required, current_user

from . import web
from app.models.base import db
from app.models.gift import Gift
from ..view_models.Trade import MyTrades
from ..view_models.gift import MyGifts


@web.route('/gifts/book/<isbn>')
@login_required
def save_to_gifts(isbn):
    if current_user.can_save_to_list(isbn):
        # 已经使用了事物
        with db.auto_commit():
            gift = Gift()
            gift.isbn = isbn
            gift.uid = current_user.id
            current_user.beans += current_app.config['BEANS_UPLOAD_ONE_BOOK']
            db.session.add(gift)
    else:
        flash('不要重复添加')

    return redirect(url_for('web.detail', isbn=isbn))


@web.route('/my/gifts')
@login_required
def my_gifts():
    gifts_of_main = Gift.get_my_gifts(current_user.id)
    isbn_list = [gift.isbn for gift in gifts_of_main]
    wish_count_list = Gift.get_wish_counts(isbn_list)
    mine_gifts = MyTrades(gifts_of_main, wish_count_list)
    return render_template('my_gifts.html', gifts=mine_gifts.trades)