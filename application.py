#!/usr/bin/env python
# encoding=utf-8
import os
import json
import datetime
from flask import Flask, render_template as _render_template, redirect,\
    url_for, request, session, make_response
from myapp.config import NAME, DEV, DEBUG, PORT, SECRET
from myapp.const import BASE_DIR
from myapp.util import is_account_exist, register_account, check_login,\
    account_email_by_aid

app = Flask(__name__)
app.secret_key = SECRET

if DEBUG:
    from werkzeug import SharedDataMiddleware
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/static': os.path.join(BASE_DIR, '../static'),
        '/external': os.path.join(BASE_DIR, '../external'),
    })

def render_template(fname, *args, **kwargs):
    kwargs['NAME'] = NAME
    kwargs['DEBUG'] = DEBUG
    kwargs['DEV'] = DEV
    return _render_template(fname, *args, **kwargs)

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home', methods=['GET', 'POST'])
def home():
    name = ''
    errmsg = ''
    if request.method == 'POST':
        email = request.form.get('email', '')
        passwd = request.form.get('passwd', '')
        aid = check_login(email, passwd)
        if aid:
            session['aid'] = aid;
            name = email
        else:
            errmsg = "Email or password mismatch."
    else:
        email = session.get('email', '')
        aid = session.get('aid', '')
        if aid:
            name = account_email_by_aid(aid)
    return render_template('home.html', email=email, errmsg=errmsg, name=name)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        from validate_email import validate_email
        errid = ''
        email = request.form.get('email', None)
        passwd = request.form.get('passwd', None)
        passwd2 = request.form.get('passwd2', None)
        remember = request.form.get('remember', None)
        if not email or not validate_email(email):
            errid = "email"
            errmsg = "Invalid email format."
        elif not passwd:
            errid = "passwd"
            errmsg = "No password entered."
        elif not passwd2:
            errid = "passwd2"
            errmsg = "No confirm password entered."
        elif passwd != passwd2:
            errid = "passwd"
            errmsg = "Two passwords are not equal."
        elif is_account_exist(email):
            errid = "email"
            errmsg = 'The email address is already registered.'
        else:
            register_account(email, passwd, remember)
            session['email'] = email
            return redirect(url_for('home'))
        return render_template('register.html', email=email, passwd=passwd,
                passwd2=passwd2, errid=errid, errmsg=errmsg)


if __name__ == '__main__':
    app.run('0.0.0.0', port=PORT, debug=DEBUG)

