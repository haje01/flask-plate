from myapp.config import NAME

def is_account_exist(email):
    return False

def register_account(email, passwd, remember):
    return
    import hashlib, uuid
    aid = redis.incr('account_cnt')
    rd_account_email = 'account:%s:email' % aid
    rd_account_salt = 'account:%s:salt' % aid
    rd_account_passwd = 'account:%s:passwd' % aid

    redis.set(rd_account_email, email)
    salt = uuid.uuid4().hex
    redis.set(rd_account_salt, salt)
    hashed_passwd = hashlib.sha512(passwd + salt).hexdigest()
    redis.set(rd_account_email, hashed_passwd)
