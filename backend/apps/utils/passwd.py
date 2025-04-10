import hashlib
# 对密码进行了简单加密（未加盐）


def verify_password(plain_password, hashed_password):
    return hashlib.sha1(plain_password.encode('utf-8')).hexdigest() == hashed_password


def get_password_hash(password):
    return hashlib.sha1(password.encode('utf-8')).hexdigest()