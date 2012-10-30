import requests
from time import time
import re
import json
import urllib.parse
import base64
import hashlib
import pickle
from bs4 import BeautifulSoup
import os

class Weibo(object):

    re_view = re.compile('view\((.+?)\)$')

    def __init__(self, email, passwd, cookie_file = "cookies.txt"):
        self.email = email
        self.passwd = passwd
        self.cookie_file = cookie_file

        self.browser = requests.session()
        self.browser.config['base_headers']['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'

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
        p = re.compile('location\.replace\(\'(.*?)\'\)')
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
        return base64.encodebytes(urllib.parse.quote(self.email).encode('UTF8')).strip()

    def enc_passwd(self, servertime, nonce):
        pwd = hashlib.sha1(self.passwd.encode('UTF8')).hexdigest()
        pwd = hashlib.sha1(pwd.encode('UTF8')).hexdigest()
        pwd = pwd + str(servertime) + str(nonce)
        pwd = hashlib.sha1(pwd.encode('UTF8')).hexdigest()
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
                    if pid1 == pid:
                        retval.append(data.get('html'))
        return retval

    def parse_user_data(self, html, tag = 'div'):
        users = []
        for fan in html.find('ul', {'class': 'cnfList'}).find_all('li'):
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
            info = fan.find(tag, {'class': 'info'})
            if info:
                user['info'] = info.text.strip()
            else:
                user['info'] = ''
            user['address'] = fan.find(tag, {'class': 'name'}).span.text.strip()
            user['face'] = self.get(fan.find(tag, {'class': 'face'}).img.get('src')).content

            yield user

    def get_users(self, url, key, re_href):
        tag = 'div'
        if url.find('my') > -1:
            tag = 'p'
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
            for user in self.parse_user_data(html, tag):
                yield user
            for a in html.find_all('a', {'href': re_href}):
                urls.append(urllib.parse.urljoin(r.url, a.get('href')))

    def get_myfans(self, uid):
        url = 'http://weibo.com/%s/myfans'%uid
        re_href = re.compile('/%s/myfans'%uid)
        key = 'pl_relation_fans'
        return self.get_users(url, key, re_href)

    def get_myfollow(self, uid):
        url = 'http://weibo.com/%s/myfollow'%uid
        re_href = re.compile('/%s/myfollow'%uid)
        key = 'pl_relation_follow'
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
