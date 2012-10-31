import requests
from time import time
import re
import json
try:
    from urlparse import urljoin
    from urllib import quote
    is_py3k = False
except:
    from urllib.parse import urljoin, quote
    is_py3k = True
import base64
from hashlib import sha1 as _sha1
def sha1(string):
    if is_py3k:
        string = string.encode('UTF8')

    return _sha1(string).hexdigest()

try:
    import cPickle as pickle
except:
    import pickle
from bs4 import BeautifulSoup
import os
import db

class Weibo(object):

    re_view = re.compile('view\((.+?)\)$')

    def __init__(self, email, passwd, cookie_file = "cookies.txt"):
        self.email = email
        self.passwd = passwd
        self.cookie_file = cookie_file

        self.browser = requests.session()
        self.browser.config['base_headers']['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'
        self.browser.config['base_headers']['Accept-Charset'] = 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'

    def set_user_agent(self, agent):
        self.browser.config['base_headers']['User-Agent'] = agent

    def load_cookies(self):
        if os.path.isfile(self.cookie_file):
            f = open(self.cookie_file, 'rb')
            self.browser.cookies = pickle.load(f)
            f.close()
            return True
        return False

    def dump_cookies(self):
        f = open(self.cookie_file, 'wb')
        pickle.dump(self.browser.cookies, f)
        f.close()

    def get(self, *args, **kws):
        return self.browser.get(*args, **kws)

    def post(self, *args, **kws):
        return self.browser.post(*args, **kws)

    def login(self):
        servertime, nonce = self.get_servertime()
        url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.3.18)'
        r = self.post(url, data={
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'vsnf': '1',
            'vsnval': '',
            'su': self.enc_user(),
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'wsse',
            'sp': self.enc_passwd(servertime, nonce),
            'encoding': 'UTF-8',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        })
        p = re.compile('location\.replace\([\'"](.*?)[\'"]\)')
        login_url = p.search(r.text).group(1)
        r = self.get(login_url)
        return r.text

    def get_servertime(self):
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=dW5kZWZpbmVk&client=ssologin.js(v1.3.18)&_=1329806375939'
        r = self.get(url)
        p = re.compile('\((.+?)\)')
        json_data = p.search(r.text).group(1)
        data = json.loads(json_data)
        servertime = data['servertime']
        nonce = data['nonce']
        return servertime, nonce

    def enc_user(self):
        if is_py3k:
            return base64.encodebytes(quote(self.email).encode('UTF8')).strip()
        return base64.encodestring(quote(self.email)).strip()

    def enc_passwd(self, servertime, nonce):
        pwd = sha1(self.passwd)
        pwd = sha1(pwd)
        pwd = pwd + str(servertime) + str(nonce)
        pwd = sha1(pwd)
        return pwd

    def get_html(self, text, pid):
        html = BeautifulSoup(text)
        retval = []
        for script in html.find_all('script'):
            if script:
                data = self.re_view.search(script.text.strip())
                if data:
                    data = data.group(1)
                    data = json.loads(data)
                    pid1 = data.get('pid')
                    if not is_py3k:
                        pid1 = pid1.encode('UTF8')
                    if pid1 == pid:
                        retval.append(data.get('html'))
        return retval

    def parse_user_data(self, html):
        users = []
        cnlist = html.find('ul', {'class': 'cnfList'})
        if cnlist:
            for fan in cnlist.find_all('li'):
                user = {}
                data = fan.get('action-data')
                if data is None:
                    continue
                for data in fan.get('action-data').split('&'):
                    data = data.split('=')
                    if data[0] == 'fnick':
                        user['nickname'] = data[1]
                    else:
                        user[data[0]] = data[1]
                info = fan.find('div', {'class': 'info'})
                if info:
                    user['info'] = info.text.strip()
                else:
                    user['info'] = ''
                addr = fan.find('div', {'class': 'name'})
                if addr and addr.span:
                    user['address'] = addr.span.text.strip()
                else:
                    user['address'] = ""
                face = fan.find('div', {'class': 'face'})
                if not db.is_exists(user['uid']) and face and face.img:
                    user['face'] = self.get(face.img.get('src')).content
                else:
                    user['face'] = b'\x00\x00'

                yield user

    def get_users(self, url, key, re_href):
        followed = []
        urls = [url]
        while True:
            if len(urls) == 0:
                break
            url = urls.pop()
            if url in followed:
                continue
            followed.append(url)
            print('Get data from [%s]'%url)
            r = self.get(url)
            html = self.get_html(r.text, key)[0]
            html = BeautifulSoup(html)
            for user in self.parse_user_data(html):
                yield user
            for a in html.find_all('a', {'href': re_href}):
                urls.append(urljoin(r.url, a.get('href')))

    def get_myfans(self, uid):
        url = 'http://weibo.com/%s/myfans'%uid
        re_href = re.compile('/%s/myfans'%uid)
        key = 'pl_relation_fans'
        return self.get_users(url, key, re_href)

    def get_myfollow(self, uid):
        url = 'http://weibo.com/%s/myfollow'%uid
        re_href = re.compile('/%s/myfollow'%uid)
        key = 'pl_relation_myfollow'
        return self.get_users(url, key, re_href)

    def get_hisfans(self, uid):
        url = 'http://weibo.com/%s/fans'%uid
        re_href = re.compile('/%s/fans'%uid)
        key = 'pl_relation_hisFans'
        return self.get_users(url, key, re_href)

    def get_hisfollow(self, uid):
        url = 'http://weibo.com/%s/follow'%uid
        re_href = re.compile('/%s/follow'%uid)
        key = 'pl_relation_hisFollow'
        return self.get_users(url, key, re_href)
