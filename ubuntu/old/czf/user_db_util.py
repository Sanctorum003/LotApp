# 对user_info.db 这个数据库的各种操作
import sqlite3 as sq
import os
import json
from ucs_db_util import search_ucs_openId_to_carID
import Time_utils as time_tool


user_db_name = 'user_info.db'

if not os.path.exists(user_db_name) :
    flag = 0 #not existed
else:
    flag = 1

try:
    conn = sq.connect(user_db_name)
    cur = conn.cursor()
except Exception as err:
    print(err)

if flag == 0:
    # cur_state => 0代表已经完成并且发送信息 ，1代表进行中， 2代表已完成但未发送信息 
    sql = """
            CREATE TABLE user_info(
                nickName   text,
                avatarUrl   text,
                gender    text,
                city      text,
                province   text,
                country    text,
                language text,
                openId    text,
                balance  double,
                start_time text,
                cur_state  int,
                Primary Key(openId)
            )
            """
    cur.execute(sql)

# 关闭这个数据库
def close_user_db():
    cur.close()
    conn.close()
    print('user_Info database has closed successfully .')

# 插入一条新的record
def insert_user_data(data,balance,st='-',cur_state=0):
    if data is '':
        return False
    try:
        cur.execute('insert into user_info(nickName,avatarUrl,gender,city,province,country,language,openId,balance,start_time,cur_state) \
        values("{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}","{9}","{10}")'.format( \
        data['nickName'],data['avatarUrl'],data['gender'],data['city'],data['province'],data['country'],data['language'],data['openId'],balance,st,cur_state))
        conn.commit()
    except Exception as err:
        print(err)
        return False
    return True

# 询问指定用户是否存在
def query_user_existed(openId):
    cur.execute('select openId from user_info where openId = "{0}" '.format(openId))
    res = cur.fetchone()
    #res: None or ('oUkv30GoL4y0lj6jUBNRK3AzJ-Yc',) 
    if not res:
        return False
    return True

# 更新指定用户的指定属性值
def update_user_data(openId,key,value):
    try:
        res = cur.execute('update user_info set '+key+'= "{0}" where openId = "{1}" '\
                    .format(value,openId))
    except Exception as err:
        print(err)
        return False
    #print('response:',res)
    #response: <sqlite3.Cursor object at 0x7f215debdb20>
    conn.commit()
    return True

# 把用户的所有信息从db中提取出来,返回一个bytes字符串 即-> "dict"
def get_user_info_from_db(openId):
    res_to_wx ={}
    db_attributes_list = ['nickName','avatarUrl','gender','city','province','country','language','openId','balance','start_time','cur_state']
    cur.execute('select * from user_info where openId = "{0}"'.format(openId))
    userInfo_query_result = cur.fetchone()

    assert( len(db_attributes_list) == len(userInfo_query_result) )
    dic_list = zip(db_attributes_list, userInfo_query_result)
    for key,value in dic_list:
        res_to_wx[key] = value

    # 增加carID
    res_to_wx['carID'] = search_ucs_openId_to_carID(openId,'carID')
    last_time = -1
    # 说明找到了
    if res_to_wx['carID'] :
        cur_Time = time_tool.get_Current_Time()
        last_time = time_tool.time_subtract(res_to_wx['start_time'], cur_Time)
    res_to_wx['last_time'] = last_time
    res_to_wx['header']='user_Info'
    return res_to_wx

# 获取用户的某一个属性的信息
def search_from_user_db(openId,key):
    cur.execute('select '+key+' from user_info where openId = "{0}"'.format(openId))
    res = cur.fetchone()
    if not res:
        return None
    return res[0]