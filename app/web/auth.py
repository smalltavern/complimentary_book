from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user

from . import web
from app.forms.auth import RegisterForm, LoginForm, ResetPasswordForm, ForgetPasswordForm
from app.models.base import db
from app.models.user import User
from app.libs.email import send_mail


@web.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        with db.auto_commit():
            user = User()
            user.set_attrs(form.data)
            db.session().add(user)

        return redirect(url_for('web.login'))

    return render_template('auth/register.html', form=form)


@web.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            url = request.args.get('next')
            if not url or not url.startswith('/'):
                url = url_for('web.index')
            return redirect(url)
        else:
            flash('账号不存在或密码错误')

    return render_template('auth/login.html', form=form)


@web.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('web.index'))


# 重置密码发送邮件页面
@web.route('/reset/password', methods=['GET', 'POST'])
def forget_password():
    form = ForgetPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first_or_404()
        # 发送重置密码邮件
        send_mail(to=form.email.data, subject='重置你的密码',
                  template='email/forget_password_request.html', user=user,
                  token=user.token_generator())
        flash("邮件已经发送了")
    return render_template('auth/forget_password_request.html', form=form)


# 重置密码页面
@web.route('/reset/password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        success = User.reset_password(token=token, pwd_raw=form.password1.data)
        if success:
            flash("你的密码已经更新啦，快去登陆吧")
            return redirect(url_for(endpoint='web.login'))
        else:
            flash("密码重置失败")
    return render_template('auth/forget_password.html', form=form)