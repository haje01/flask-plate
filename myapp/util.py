import redis
from myapp.config import NAME, DB_NO
import os
from urlparse import urlparse, urljoin
from flask import request, url_for, redirect
from flaskext.babel import gettext
import formencode
from formencode import validators
from myapp.config import NAME


FIXEDSALT = '36234c3f0a1b4392b5159c68b6c90203'

redis = redis.Redis(db = DB_NO)
_ = gettext

def is_account_exist(email):
    rd_account_email = 'account_emails'
    return redis.sismember(rd_account_email, email)

def digest_passwd(email, passwd):
    import hashlib
    salt = email + FIXEDSALT
    return hashlib.sha512(passwd + salt).hexdigest()

def register_account(email, passwd):
    nid = redis.incr('account_cnt')
    rd_account_email = 'account:%s:email' % nid
    rd_account_passwd = 'account:%s:passwd' % nid

    redis.set(rd_account_email, email)
    salt = email + FIXEDSALT
    redis.set(rd_account_email, email)
    redis.set(rd_account_passwd, digest_passwd(email, passwd))
    redis.sadd('account_emails', email)
    redis.hset('account_id_map', email, nid)

def check_login(email, _passwd):
    nid = redis.hget('account_id_map', email)
    if not nid:
        return
    rd_account_email = 'account:%s:email' % nid
    rd_account_passwd = 'account:%s:passwd' % nid

    email = redis.get(rd_account_email)
    if not email:
        return
    passwd = redis.get(rd_account_passwd)
    if digest_passwd(email, _passwd) == passwd:
        return nid
    else:
        return

def account_email_by_nid(nid):
    rd_account_email = 'account:%s:email' % nid
    return redis.get(rd_account_email)

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

def remove_account_by_email(email):
    nid = redis.hget('account_id_map', email)
    return remove_account_by_nid(nid)

def remove_account_by_nid(nid):
    rd_account_email = 'account:%s:email' % nid
    email = redis.get(rd_account_email)
    rd_account_passwd = 'account:%s:passwd' % nid
    redis.delete(rd_account_email)
    redis.delete(rd_account_passwd)
    redis.srem('account_emails', email)
    redis.hdel('account_id_map', email)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

def redirect_back(endpoint, **values):
    target = request.form.get('next', '')
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)

class UniqueEmail(formencode.FancyValidator):
    def _convert_to_python(self, value, state):
        validators.Email().to_python(value)
        if is_account_exist(value):
            raise formencode.Invalid(_('That email is already exists'), value,
                    state)
        return value

class RegisterSchema(formencode.Schema):
    email = UniqueEmail()
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


