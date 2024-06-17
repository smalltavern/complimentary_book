from threading import Thread
from flask import current_app, render_template
from flask_mail import Message


def send_async_email(app, msg):
    from app import mail
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            pass


def send_mail(to, subject, template, **kwargs):
    # msg = Message('测试邮件', sender='guaosi@vip.qq.com', body='test', recipients=['527992744@qq.com'])

    msg = Message('[i换书]' + '' + subject, sender=current_app.config['MAIL_USERNAME'], recipients=[to])
    msg.html = render_template(template, **kwargs)
    # current_app 是一个代理对象
    # 下面代码可以获取 falsk 的真实核心对象
    app = current_app._get_current_object()

    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
