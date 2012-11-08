from config import EMAIL, PASSWD, COOKIE_FILE, UID
from weibo import Weibo
import db
import os
import random
from time import sleep as _sleep

import requests_cache
requests_cache.configure('cache')

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
        print('User[%s] fan[%s]'%(uid, fan['uid']))
        db.add_user(fan['uid'], fan['nickname'], fan['sex'], fan['address'], fan['info'], fan['face'])
        db.add_relation(uid, fan['uid'])
    follow = []
    for fo in weibo.get_hisfollow(uid):
        follow.append(fo['uid'])
        print('User[%s] follow[%s]'%(uid, fo['uid']))
        db.add_user(fo['uid'], fo['nickname'], fo['sex'], fo['address'], fo['info'], fo['face'])
        db.add_relation(fo['uid'], uid)
    for friend in get_friends(fans, follow):
        db.add_queue(friend)
    print('User[%s] fans[%s] follow[%s]'%(uid, len(fans), len(follow)))
    db.finish_queue(uid)

def run():
    liveness = 0
    while True:
        try:
            liveness += 1
            uid = db.get_next_queue()
            print('Get user[%s]\' relationship'%uid)
            get_relation(uid)
            if liveness <= 50:
                delay = random.randint(5, 60)
            elif liveness<=100:
                delay = random.randint(30, 180)
            else:
                delay = random.randint(600, 1800)
                if delay > 900:
                    liveness = 0
            _sleep(delay)
            requests_cache.clear()
        except Exception as e:
            print('Error:%s'%e)
            _sleep(300)

def first_run():
    print('Login')
    login()
    print('Create table')
    #db.create_table()
    print('Get my relation')
    #get_myrelation()
    with open('First_run', 'w') as f:
        f.write('0')

def main():
    if not os.path.isfile('First_run'):
        first_run()
    run()

if __name__ == '__main__':
    main()
