import redis
from myapp.config import NAME, DB_NO
import os

FIXEDSALT = '36234c3f0a1b4392b5159c68b6c90203'

redis = redis.Redis(db = DB_NO)

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
        return None
    rd_account_email = 'account:%s:email' % nid
    rd_account_passwd = 'account:%s:passwd' % nid

    email = redis.get(rd_account_email)
    passwd = redis.get(rd_account_passwd)
    if digest_passwd(email, _passwd) == passwd:
        return nid
    else:
        return None

def account_email_by_nid(nid):
    rd_account_email = 'account:%s:email' % nid
    return redis.get(rd_account_email)

def get_secret_key():
    if not redis.exists('app_secret_key'):
        redis.set('app_secret_key', os.urandom(24))
    return redis.get('app_secret_key')

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
    rd_account_passwd = 'account:%s:passwd' % nid
    redis.delete(rd_account_email)
    redis.delete(rd_account_passwd)

