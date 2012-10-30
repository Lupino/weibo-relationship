from config import *
from weibo import Weibo
import db
import os

weibo = Weibo(EMAIL, PASSWD, COOKIE_FILE)

weibo.load_cookies()

def login():
    weibo.login()
    weibo.dump_cookies()

def get_friends(fans, follow):
    friends = []
    for fan in fans:
        for fo in follow:
            if fan == fo:
                friends.append(fan)
                break
    return friends

def get_myrelation():
    db.add_queue(UID)
    fans = []
    for fan in weibo.get_myfans(UID):
        fans.append(fan['uid'])
        db.add_user(fan['uid'], fan['nickname'], fan['sex'], fan['address'], fan['info'], fan['face'])
        db.add_relation(UID, fan['uid'])
    follow = []
    for fo in weibo.get_myfollow(UID):
        follow.append(fo['uid'])
        db.add_user(fo['uid'], fo['nickname'], fo['sex'], fo['address'], fo['info'], fo['face'])
        db.add_relation(fo['uid'], UID)
    for friend in get_friends(fans, follow):
        db.add_queue(friend)
    db.finish_queue(UID)

def get_relation(uid):
    fans = []
    for fan in weibo.get_hisfans(uid):
        fans.append(fan['uid'])
        db.add_user(fan['uid'], fan['nickname'], fan['sex'], fan['address'], fan['info'], fan['face'])
        db.add_relation(uid, fan['uid'])
    follow = []
    for fo in weibo.get_hisfollow(uid):
        follow.append(fo['uid'])
        db.add_user(fo['uid'], fo['nickname'], fo['sex'], fo['address'], fo['info'], fo['face'])
        db.add_relation(fo['uid'], uid)
    for friend in get_friends(fans, follow):
        db.add_queue(friend)
    db.finish_queue(uid)

def run():
    while True:
        uid = db.get_next_queue()
        get_relation(uid)

def first_run():
    login()
    db.create_table()
    get_myrelation()
    open('First_run', 'w') as f:
        f.write(0)

def main():
    if not os.path.isfile('First_run'):
        first_run()
    run()

if __name__ == '__main__':
    main()
