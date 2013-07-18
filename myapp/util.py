import redis as _redis
from myapp.config import NAME, DB_NO
import os
from urlparse import urlparse, urljoin
from flask import request, url_for, redirect, session
from flaskext.babel import gettext
import formencode
from formencode import validators
from myapp.config import NAME
from functools import wraps
from myapp.make_config import make_config


FIXEDSALT = '36234c3f0a1b4392b5159c68b6c90203'

cfg = make_config()
redis = _redis.Redis(db = cfg['DB_NO'])
_ = gettext

def is_account_exist(_id):
    rd_account_ids = 'account_ids'
    return redis.sismember(rd_account_ids, _id)

def digest_passwd(email, passwd):
    import hashlib
    salt = email + FIXEDSALT
    return hashlib.sha512(passwd + salt).hexdigest()

def register_account(_id, email, passwd):
    nid = redis.incr('account_cnt')
    rd_account_id = 'account:%s:id' % nid
    rd_account_email = 'account:%s:email' % nid
    rd_account_passwd = 'account:%s:passwd' % nid

    redis.set(rd_account_id, _id)
    redis.set(rd_account_email, email)
    redis.set(rd_account_passwd, digest_passwd(_id, passwd))
    redis.sadd('account_ids', _id)
    redis.hset('account_id_map', _id, nid)

def check_login(_id, _passwd):
    nid = redis.hget('account_id_map', _id)
    if not nid:
        return
    rd_account_id = 'account:%s:id' % nid
    rd_account_passwd = 'account:%s:passwd' % nid
    passwd = redis.get(rd_account_passwd)
    if digest_passwd(_id, _passwd) == passwd:
        return nid
    else:
        return

def account_id_by_nid(nid):
    rd_account_id = 'account:%s:email' % nid
    return redis.get(rd_account_id)

def get_secret_key():
    if not redis.exists('app_secret_key'):
        redis.set('app_secret_key', os.urandom(24))
    return redis.get('app_secret_key')

def reset_secret_key():
    redis.set('app_secret_key', os.urandom(24))

def confirm(prompt=None, resp=False):
    """prompts for yes or no response from the user. Returns True for yes and
    False for no.

    'resp' should be set to the default value assumed by the caller when
    user simply types ENTER.

    >>> confirm(prompt='Create Directory?', resp=True)
    Create Directory? [y]|n: 
    True
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: 
    False
    >>> confirm(prompt='Create Directory?', resp=False)
    Create Directory? [n]|y: y
    True

    """
    
    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')
        
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

def remove_account_by_id(_id):
    nid = redis.hget('account_id_map', _id)
    return remove_account_by_nid(nid)

def remove_account_by_nid(nid):
    rd_account_id = 'account:%s:id' % nid
    rd_account_email = 'account:%s:email' % nid
    rd_account_passwd = 'account:%s:passwd' % nid
    redis.delete(rd_account_id)
    redis.delete(rd_account_email)
    redis.delete(rd_account_passwd)
    _id = redis.get(rd_account_id)
    redis.srem('account_ids', _id)
    redis.hdel('account_id_map', _id)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target(referrer = False):
    targets = [request.values.get('next')]
    if referrer: # need when using login page
        targets.append(request.referrer)
    for target in targets:
        if not target:
            continue
        if is_safe_url(target):
            return target

def redirect_back(endpoint, **values):
    target = request.form.get('next', '')
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)

class UniqueID(formencode.FancyValidator):
    def _convert_to_python(self, value, state):
        if is_account_exist(value):
            raise formencode.Invalid(_('That ID is already exists'), value,
                    state)
        return value

class RegisterSchema(formencode.Schema):
    id = UniqueID()
    email = validators.Email(not_empty = True)
    passwd = validators.String(not_empty = True)
    passwd2 = validators.String(not_empty = True)
    remember = validators.Bool()
    chained_validators = [validators.FieldsMatch('passwd', 'passwd2')]

def validate_register(fields):
    errors = None
    try:
        fields = RegisterSchema.to_python(fields)
    except validators.Invalid, e:
        errors = dict((k, v) for k, v in
            e.unpack_errors().iteritems())
    return fields, errors

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        name = session.get('aname', '')
        if not name:
            return redirect(url_for('home', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
 
