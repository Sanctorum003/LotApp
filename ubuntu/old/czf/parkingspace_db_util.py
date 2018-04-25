# 对parkingspace.db 这个数据库的各种操作
import sqlite3 as sq
import os
import json

parking_db_name = 'parkingspace.db'

if not os.path.exists(parking_db_name) :
    flag = 0 #not existed
else:
    flag = 1

try:
    conn = sq.connect(parking_db_name)
    cur = conn.cursor()
except Exception as err:
    print(err)

if flag == 0:
    sql = """
            CREATE TABLE ps_info(
                carID   int,
                openning  bool,
                occupied  bool,
                start_time text,
                Primary Key(carID)
            )
            """
    cur.execute(sql)

# 关闭这个数据库
def close_parking_db():
    cur.close()
    conn.close()
    print('parkingspace database has closed successfully .')

# 插入一条新的record
def insert_parking_data(carID,op,oc,st):
    try:
        cur.execute('insert into ps_info(carID,openning,occupied,start_time) \
        values("{0}","{1}","{2}","{3}")'.format(carID,op,oc,st))
        conn.commit()
    except Exception as err:
        print(err)
        return False
    return True

# 询问指定车位信息是否存在
def query_parking_existed(carID):
    cur.execute('select openId from ps_info where carID = "{0}" '.format(carID))
    res = cur.fetchone()
    #res: None or ('oUkv30GoL4y0lj6jUBNRK3AzJ-Yc',) 
    if not res:
        return False
    return True

# 更新指定车位的指定属性值
def update_parking_data(carID,key,value):
    try:
        res = cur.execute('update ps_info set '+key+'= "{0}" where carID = "{1}" '\
                    .format(value,carID))
    except Exception as err:
        print(err)
        return False
    #print('response:',res)
    #response: <sqlite3.Cursor object at 0x7f215debdb20>
    conn.commit()
    return True

# 获取车位的某一个属性的信息
def search_from_ps_db(carID,key):
    cur.execute('select '+key+' from ps_info where carID = "{0}"'.format(carID))
    res = cur.fetchone()
    if not res:
        return None
    # if res[0] == 'True' or res[0] == 'False':
    #     return eval(res[0])    
    return res[0]