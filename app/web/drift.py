from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

from . import web
from ..forms.book import DriftForm
from ..libs.email import send_mail
from ..models.base import db
from ..models.drift import Drift
from ..models.gift import Gift
from ..view_models.book import BookViewModel


# 发起请求书籍接口
@web.route('/drift/<gid>', methods=['GET', "POST"])
@login_required
def send_drift(gid):
    """
    自己不能向自己请求数据
    鱼豆必须足够（大于等于 1）
    每索取两本书，自己就必须送出一本书
    :return:
    """
    gift = Gift.query.get_or_404(gid)
    if gift.is_yourself_gift(current_user.id):
        flash('这本书是你自己的，不能向自己索要')
        return redirect(url_for('web.detail', isbn=gift.isbn))

    can = current_user.can_send_drift()
    if not can:
        return render_template('not_enouth_beans.html', beans=current_user.beans)

    form = DriftForm(request.form)
    if request.method == 'POST' and form.validate():
        save_drift(form, gift)
        send_mail(to=gift.user.email, subject='有人想要一本书', template='email/get_gift.html', wisher=current_user,
                  gift=gift)
        return redirect(url_for(endpoint='web.pending'))

    gifter = gift.user.summary
    return render_template('drift.html', form=form, gifter=gifter, user_beans=current_user.beans)


@web.route('/pending')
@login_required
def pending():
    drifts = Drift.query.filter_by()
    return render_template('pending.html')


def save_drift(drift_form, current_gift):
    with db.auto_commit():
        drift = Drift()
        # 类似于 laravel 中的 request()->validate()
        drift_form.populate_obj(drift)

        drift.gift_id = current_gift.id
        drift.requester_id = current_user.id
        drift.requester_nickname = current_user.nickname
        drift.gifter_nickname = current_gift.user.nickname
        drift.gifter_id = current_gift.user.id

        book = BookViewModel(current_gift.book)

        drift.book_title = book.title
        drift.book_author = book.author
        drift.book_img = book.image
        drift.isbn = book.isbn

        current_user.beans -= 1

        db.session.add(drift)