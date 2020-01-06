#coding=utf-8

import time

def create_db():
    import sqlite3
    conn = sqlite3.connect('proxies.db')
    cursor = conn.cursor()
    sql = "create table proxies_table (protocol varchar, ip varchar, port varchar, quality varchar, findtime varchar, updatetime varchar)"
    cursor.execute(sql)
    cursor.close()

def get_proxy(conn,num=None,col='*'):
    cursor = conn.cursor()
    sql = "select %s from proxies_table order by quality" % col
    if num:
        sql += " limit " + str(num)
    cursor.execute(sql)
    values = cursor.fetchall()
    return values

def del_proxy(conn,proxy):
    cursor = conn.cursor()
    sql = "delete from proxies_table where ip='%s'" % (proxy['ip'])
    cursor.execute(sql)
    conn.commit()

def insert_proxy(conn,proxy):
    cursor = conn.cursor()
    inserttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    data = "'%s','%s','%s','%s','%s','%s'" % (proxy['protocol'],proxy['ip'],proxy['port'],proxy['quality'],inserttime,inserttime)
    sql = 'insert into proxies_table (protocol,ip,port,quality,findtime,updatetime) values (%s)' % data
    cursor.execute(sql)
    conn.commit()

def update_proxy(conn,proxy):
    cursor = conn.cursor()
    updatetime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    sql = "update proxies_table set quality='%s',updatetime='%s' where ip='%s'" % (proxy['quality'],updatetime,proxy['ip'])
    cursor.execute(sql)