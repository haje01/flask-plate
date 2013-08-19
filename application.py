#!/usr/bin/env python
# encoding=utf-8
import os
from flask import Flask, render_template as _render_template, redirect,\
    url_for, request, session
from flaskext.babel import Babel
import formencode
from formencode import htmlfill
from datetime import timedelta
from myapp.make_config import make_config
from myapp.util import register_account, check_login, get_secret_key,\
    redirect_back, validate_register, _, get_redirect_target, auth_required

app = Flask(__name__)
make_config(app)
app.secret_key = get_secret_key()
app.permanent_session_lifetie = timedelta(days=1)
babel = Babel(app)
formencode.api.set_stdtranslation(domain="FormEncode",
                                  languages=[app.config['LANG']])

DEBUG_PORT = 8000

if app.debug:
    from werkzeug import SharedDataMiddleware
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/static': os.path.join(app.root_path, 'static'),
        '/external': os.path.join(app.root_path, 'external'),
    })


def render_template(fname, *args, **kwargs):
    kwargs['NAME'] = app.config['NAME']
    kwargs['DEBUG'] = app.debug
    kwargs['DEV'] = app.config['DEV']
    kwargs['LANG'] = app.config['LANG']
    kwargs['active'] = fname.split('.')[0]
    kwargs['aname'] = session.get('aname', '')
    return _render_template(fname, *args, **kwargs)


@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/home', methods=['GET', 'POST'])
def home():
    errmsg = ''
    _id = ''
    next = get_redirect_target()
    if request.method == 'POST':
        _id = request.form.get('id', '')
        passwd = request.form.get('passwd', '')
        remember = request.form.get('remember', '')
        _id, errmsg = login(session, _id, passwd, remember)
        if not errmsg:
            return redirect_back('home')
    else:
        remember = session.get('remember', '')
        if remember:
            _id = session.get('id')
    return render_template('home.html', _id=_id, errmsg=errmsg,
                           remember=remember, next=next)


def login(session, _id, passwd, remember):
    errmsg = ''
    session['remember'] = remember
    if remember:
        session['id'] = _id
    else:
        session['id'] = None
    nid = check_login(_id, passwd)
    if nid:
        session['nid'] = nid
        session['aname'] = _id
    else:
        errmsg = _("ID or password mismatch")
    return _id, errmsg


@app.route('/about')
@auth_required
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        fields, errors = validate_register(request.form)
        if errors:
            tmpl = render_template('register.html')
            return htmlfill.render(tmpl, defaults=fields, errors=errors)
        else:
            _id = fields.get('id')
            email = fields.get('email')
            remember = fields.get('remember')
            passwd = fields.get('passwd')
            register_account(_id, email, passwd)
            login(session, _id, passwd, remember)
        return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session['aname'] = None
    session['nid'] = None
    return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(e):
    return _render_template('404.html'), 404

if __name__ == '__main__':
    app.run('0.0.0.0', port=DEBUG_PORT)
