from config import DBFILE
import sqlite3 as sqlite

def create_table():
    conn = sqilte.connect(DBFILE)
    cur = conn.cursor()
    cur.execute('''
            create table user (
            id integer primary key autoincrement,
            uid int(10),
            nickname varchar(100),
            sex varchar(1),
            blog varchar(100),
            birthday varchar(30),
            site varchar(30),
            email varchar(50),
            qq varchar(50),
            info varchar(300)
            )
            ''')
    cur.execute('''
            create table relation (
            me int(10),
            fan int(10)
            )
            ''')
    cur.execute('''
            create table queue(
            id integer primary key autoincrement,
            user_id int(10),
            act varchar(1),
            is_finish varchar(1)
            )
            ''')
    conn.commit()
    cur.close()
    conn.close()

def is_exists(uid):
    conn = sqlite.connect(DBFILE)
    cur = conn.cursor()
    cur.execute("select uid from user where uid = ?", (uid, ))
    ret = cur.fetchone()
    retval = False
    if ret:
        retval = True
    cur.close()
    conn.close()
    return retval

def add_relation(me, fan):
    conn = sqlite.connect(DBFILE)
    cur = conn.cursor()
    cur.execute("select * from relation where me = ? and fan = ?", (me, fan, ))
    ret = cur.fetchone()
    if ret is None:
        cur.execute('insert into relation (me, fan)values(?, ?)', (me, fan))
        conn.commit()
    cur.close()
    conn.close()

def get_relation(me):
    conn = sqlite.connect(DBFILE)
    cur = conn.cursor()
    cur.execute("select fan from relation where me = ?", (me, ))
    retval = []
    for fan in cur.fetchall():
        retval.append(fan[0])
    cur.close()
    conn.close()
    return retval

def get_user(id):
    conn = sqlite.connect(DBFILE)
    cur = conn.cursor()
    cur.execute("select uid, nickname, sex, blog, birthday, site, email, qq, info from user where id = ?", (id, ))
    ret = cur.fetchone()
    retval = {}
    if ret:
        retval['uid'] = ret[0]
        retval['nickname'] = ret[1]
        retval['sex'] = ret[2]
        retval['blog'] = ret[3]
        retval['birthday'] = ret[4]
        retval['site'] = ret[5]
        retval['email'] = ret[6]
        retval['qq'] = ret[7]
        retval['info'] = ret[8]
    cur.close()
    conn.close()
    return retval

def add_user(uid, nickname, sex, blog, birthday, site, email, qq, info):
    conn = sqilte.connect(DBFILE)
    cur = conn.cursor()
    cur.execute('insert into user (uid, nickname, sex, blog, birthday, site, email, qq, info)values(?, ?, ?, ?, ?, ?, ?, ?, ?)', (uid, nickname, sex, blog, birthday, site, email,  qq, info, ))
    conn.commit()
    cur.close()
    conn.close()
