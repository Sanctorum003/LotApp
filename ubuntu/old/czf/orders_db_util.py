# 对orders_db_util.db 这个数据库的各种操作
import sqlite3 as sq
import os
import json
from ucs_db_util import search_ucs_openId_to_carID
import Time_utils as time_tool


order_db_name = 'orders.db'

if not os.path.exists(order_db_name) :
    flag = 0 #not existed
else:
    flag = 1

try:
    conn = sq.connect(order_db_name)
    cur = conn.cursor()
except Exception as err:
    print(err)

if flag == 0:
    # cur_state => 0代表已经完成并且发送信息 ，1代表进行中， 2代表已完成但未发送信息 
    sql = """
            CREATE TABLE orders(
                openId  text,
                start_time text,
                stop_time text,
                cur_state  int,
                cost   double,
                last_time int,
                Primary Key(openId,start_time)
            )
            """
    cur.execute(sql)

# 关闭这个数据库
def close_orders_db():
    cur.close()
    conn.close()
    print('orders database has closed successfully .')

# 插入一条新的record
def insert_orders_data(data):
    try:
        cur.execute('insert into orders(openId,start_time,stop_time,cur_state,cost,last_time) \
        values("{0}","{1}","{2}","{3}","{4}","{5}")'.format( \
        data['openId'],data['start_time'],data['stop_time'],data['cur_state'],data['cost'],data['last_time']))
        conn.commit()
    except Exception as err:
        print(err)
        return False
    return True

# 询问指定用户是否存在
def query_orders_existed(openId,start_time):
    cur.execute('select openId from orders where openId = "{0}" and start_time = "{1}" '.format(openId,start_time))
    res = cur.fetchone()
    #res: None or ('oUkv30GoL4y0lj6jUBNRK3AzJ-Yc',) 
    if not res:
        return False
    return True

# 更新指定用户的指定属性值
def update_orders_data(openId,start_time,key,value):
    try:
        res = cur.execute('update orders set '+key+'= "{0}" where openId = "{1}" and start_time = "{2}" '\
                    .format(value,openId,start_time))
    except Exception as err:
        print(err)
        return False
    #print('response:',res)
    #response: <sqlite3.Cursor object at 0x7f215debdb20>
    conn.commit()
    return True

# 把用户的所有信息从db中提取出来,返回一个bytes字符串 即-> "dict"
def get_one_order_from_db(openId):
    res_to_wx ={}
    db_attributes_list = ['openId','start_time','stop_time','cur_state','cost','last_time']
    cur.execute('select * from orders where openId = "{0}" and cur_state = "{1}" '.format(openId,3))
    query_result = cur.fetchone()
    print('query_result:',query_result)
    assert( len(db_attributes_list) == len(query_result) )
    print('====*-*====')
    dic_list = zip(db_attributes_list, query_result)
    for key,value in dic_list:
        res_to_wx[key] = value

    '''
    # 增加carID
    res_to_wx['carID'] = search_ucs_openId_to_carID(openId,'carID')
    last_time = -1
    # 说明找到了
    if res_to_wx['carID'] :
        cur_Time = time_tool.get_Current_Time()
        last_time = time_tool.time_subtract(res_to_wx['start_time'], cur_Time)
    res_to_wx['last_time'] = last_time
    res_to_wx['header']='orders'
    '''

    return res_to_wx

# 获取用户的某一个属性的信息
def search_from_order_db(openId,st,key):
    cur.execute('select '+key+' from orders where openId = "{0}" and start_time = "{1}" '.format(openId,st))
    res = cur.fetchone()
    if not res:
        return None
    return res[0]

def update_all_finished_order(openid):
    try:
        res = cur.execute('update orders set cur_state = "{0}" where openId = "{1}" '\
                    .format(0,openid))
    except Exception as err:
        print(err)
        return False
    #print('response:',res)
    #response: <sqlite3.Cursor object at 0x7f215debdb20>
    conn.commit()
    return True

def get_history_orders(openid):
    try:
        cur.execute('select start_time,stop_time,cost,last_time from orders where openId = "{0}"'.format(openid))
    except Exception as err:
        print(err)
    res = cur.fetchall()
    return res

# test:
# import time 

# data = {}
# data['openId'] = 'xxx'
# data['start_time'] = time_tool.get_Current_Time()
# time.sleep(5)
# data['stop_time'] = time_tool.get_Current_Time()
# data['cost'] = time_tool.time_subtract(data['start_time'],data['stop_time'])
# data['last_time'] = data['cost']
# data['cur_state'] = 0

# insert_orders_data(data)

# print(search_from_order_db(data['openId'],data['start_time'],'cost'))
# print( get_one_order_from_db(data['openId'],data['start_time']) )
# print(query_orders_existed(data['openId'],data['start_time']))