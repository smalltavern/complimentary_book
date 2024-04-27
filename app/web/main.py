from flask import render_template

from app.models.gift import Gift
from app.view_models.book import BookViewModel
from app.web import web


@web.route('/')
def index():
    recent = Gift.recent()
    books = [BookViewModel(signal.book) for signal in recent]

    return render_template('index.html', books=books)