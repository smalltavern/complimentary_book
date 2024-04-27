from app.web import web
from flask_login import login_required


@web.route('/personal')
@login_required
def personal():
    return 'personal'