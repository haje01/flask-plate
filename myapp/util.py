import redis
from myapp.config import NAME, DB_NO

FIXEDSALT = '36234c3f0a1b4392b5159c68b6c90203'

redis = redis.Redis(db = DB_NO)

def is_account_exist(email):
    rd_account_email = 'account_emails'
    return redis.sismember(rd_account_email, email)

def register_account(email, passwd, remember):
    import hashlib, uuid
    aid = redis.incr('account_cnt')
    rd_account_email = 'account:%s:email' % aid
    rd_account_passwd = 'account:%s:passwd' % aid

    redis.set(rd_account_email, email)
    salt = email + FIXEDSALT
    hashed_passwd = hashlib.sha512(passwd + salt).hexdigest()
    redis.set(rd_account_email, email)
    redis.set(rd_account_passwd, hashed_passwd)
    redis.sadd('account_emails', email)
