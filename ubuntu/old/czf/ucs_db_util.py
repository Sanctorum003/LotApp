# 对which_carspace.db 这个数据库的各种操作
import sqlite3 as sq
import os
import json

db_name = 'which_carspace.db'

if not os.path.exists(db_name) :
    flag = 0 #not existed
else:
    flag = 1

try:
    conn = sq.connect(db_name)
    cur = conn.cursor()
except Exception as err:
    print(err)

# msg['header'] = 'timer_stop'
#         msg['cost'] = cost_money
#         msg['last_time'] = sec
#         msg['current_time'] = stop_Time
#         msg['current_money'] = balance

if flag == 0:
    sql = """
            CREATE TABLE user_to_carspace(
                openId    text,
                carID     int,
                Primary Key(openId)
            )
            """
    cur.execute(sql)

# 插入一条新的record
def insert_ucs_data(openId,carID):
    try:
        cur.execute('insert into user_to_carspace(openId,carID) values("{0}","{1}")'.format(openId, carID))
        conn.commit()
    except Exception as err:
        print(err)
        return False
    return True

# 询问指定用户是否存在
def query_ucs_existed(openId):
    cur.execute('select openId from user_to_carspace where openId = "{0}" '.format(openId))
    res = cur.fetchone()
    #res: None or ('oUkv30GoL4y0lj6jUBNRK3AzJ-Yc',) 
    if not res:
        return False
    return True

# 更新指定用户的carID
def update_ucs_data(openId,key,value):
    try:
        res = cur.execute('update user_to_carspace set '+key+'= "{0}" where openId = "{1}" '\
                    .format(value,openId))
    except Exception as err:
        print(err)
        return False
    #print('response:',res)
    #response: <sqlite3.Cursor object at 0x7f215debdb20>
    conn.commit()
    return True

# 查询指定ID的carID
def search_ucs_openId_to_carID(openId,key):
    cur.execute('select '+key+' from user_to_carspace where openId = "{0}"'.format(openId))
    res = cur.fetchone()
    if not res:
        return None
    return res[0]

# 查询指定ID的carID
def search_ucs_carID_to_openId(carID,key):
    cur.execute('select '+key+' from user_to_carspace where carID = "{0}"'.format(carID))
    res = cur.fetchone()
    if not res:
        return None
    return res[0]

# 删除一个用户信息
def delete_ucs_data(openId):
    try:
        cur.execute('delete from user_to_carspace where openId = "{0}"'.format(openId))
    except Exception:
        return False
    conn.commit()
    return True