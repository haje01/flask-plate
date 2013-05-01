#!/usr/bin/env python
# encoding=utf-8
import os
import json
import datetime
from flask import Flask, render_template as _render_template, redirect,\
    url_for, request, session
from myapp.config import NAME, DEV, DEBUG, PORT, SECRET
from myapp.const import BASE_DIR
from myapp.util import is_account_exist, register_account

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

@app.route('/home')
def home():
    email = session.get('email', '')
    return render_template('home.html', email=email)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        from validate_email import validate_email
        errid = ''
        email = request.form.get('email', None)
        passwd = request.form.get('passwd', None)
        remember = request.form.get('remember', None)
        if not email or not validate_email(email):
            errid = "email"
            errmsg = "Invalid email format."
        elif not passwd:
            errid = "passwd"
            errmsg = "No password entered."
        elif is_account_exist(email):
            errid = "email"
            errmsg = 'The email address is already registered.'
        else:
            register_account(email, passwd, remember)
            session['email'] = email
            return redirect(url_for('home'))
        return render_template('register.html', email=email, passwd=passwd, errid=errid, errmsg=errmsg)

if __name__ == '__main__':
    app.run('0.0.0.0', port=PORT, debug=DEBUG)

