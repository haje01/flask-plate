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
    aid = redis.incr('account_cnt')
    rd_account_email = 'account:%s:email' % aid
    rd_account_passwd = 'account:%s:passwd' % aid

    redis.set(rd_account_email, email)
    salt = email + FIXEDSALT
    redis.set(rd_account_email, email)
    redis.set(rd_account_passwd, digest_passwd(email, passwd))
    redis.sadd('account_emails', email)
    redis.hset('account_id_map', email, aid)

def check_login(email, _passwd):
    aid = redis.hget('account_id_map', email)
    if not aid:
        return None
    rd_account_email = 'account:%s:email' % aid
    rd_account_passwd = 'account:%s:passwd' % aid

    email = redis.get(rd_account_email)
    passwd = redis.get(rd_account_passwd)
    if digest_passwd(email, _passwd) == passwd:
        return aid
    else:
        return None

def account_email_by_aid(aid):
    rd_account_email = 'account:%s:email' % aid
    return redis.get(rd_account_email)

def get_secret_key():
    if not redis.exists('app_secret_key'):
        redis.set('app_secret_key', os.urandom(24))
    return redis.get('app_secret_key')

