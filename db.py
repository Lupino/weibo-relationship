from config import DBFILE
import sqlite3 as sqlite

def create_table():
    conn = sqlite.connect(DBFILE)
    cur = conn.cursor()
    cur.execute('''
            create table user (
            id integer primary key autoincrement,
            uid int(10),
            nickname varchar(100),
            sex varchar(1),
            address varchar(300),
            info varchar(300),
            face
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
            uid int(10),
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
    cur.execute("select uid, nickname, sex, address, info, face from user where id = ?", (id, ))
    ret = cur.fetchone()
    retval = {}
    if ret:
        retval['uid'] = ret[0]
        retval['nickname'] = ret[1]
        retval['sex'] = ret[2]
        retval['address'] = ret[3]
        retval['info'] = ret[4]
        retval['face'] = ret[5]
    cur.close()
    conn.close()
    return retval

def add_user(uid, nickname, sex, address, info, face):
    conn = sqlite.connect(DBFILE)
    cur = conn.cursor()
    cur.execute("select uid from user where uid = ?", (uid, ))
    ret = cur.fetchone()
    if ret is None:
        cur.execute('insert into user (uid, nickname, sex, address, info, face)values(?, ?, ?, ?, ?, ?)', (uid, nickname, sex, address, info, face, ))
        conn.commit()
    cur.close()
    conn.close()

def add_queue(uid):
    conn = sqlite.connect(DBFILE)
    cur = conn.cursor()
    cur.execute('select id from queue where uid = ?', (uid, ))
    ret = cur.fetchone()
    if ret is None:
        cur.execute('insert into queue (uid, is_finish)values(?, ?)', (uid, 'N', ))
        conn.commit()
    cur.close()
    conn.close()

def get_next_queue():
    conn = sqlite.connect(DBFILE)
    cur = conn.cursor()
    cur.execute('select uid from queue where is_finish = ? order by id', ('N', ))
    ret = cur.fetchone()
    cur.close()
    conn.close()
    return ret[0]

def finish_queue(uid):
    conn = sqlite.connect(DBFILE)
    cur = conn.cursor()
    cur.execute('update queue set is_finish = ? where uid = ?', ('Y', uid, ))
    conn.commit()
    cur.close()
    conn.close()

