from twisted.internet import protocol as po
from autobahn.twisted.websocket import WebSocketServerFactory,\
                                        WebSocketServerProtocol
import sys
import Time_utils as time_tool
from twisted.python import log
import requests
import json
from WXBizDataCrypt import WXBizDataCrypt

import time

from user_db_util import insert_user_data,\
                        query_user_existed,\
                          update_user_data,\
                          close_user_db,\
                          get_user_info_from_db,\
                          search_from_user_db

# ucs = User to Car Space
from ucs_db_util import update_ucs_data,\
                             search_ucs_openId_to_carID,\
                             insert_ucs_data,\
                             query_ucs_existed,\
                             delete_ucs_data,\
                             search_ucs_carID_to_openId

from parkingspace_db_util import insert_parking_data,\
                                 query_parking_existed,\
                                 update_parking_data,\
                                 search_from_ps_db

from orders_db_util import *

from Arm_decryot import *

# 车位到微信用户的映射  CarID => 微信对象self
carID_to_Wx = {}

# 微信小程序的相关信息
appid='wxf9c31c349c55f503'
secret='c318b212a9348bc11a299755fdbdf659'
grant_type='authorization_code'

url = 'https://api.weixin.qq.com/sns/jscode2session'
param = {
        'appid':appid,
        'secret':secret,
        'grant_type':grant_type,
        'js_code':''
        }


# 和微信小程序的通信协议
class WxProtocol(WebSocketServerProtocol):
    '''
    @self.res_info 是一个如下的Json:
    {
        'userInfo':{
                        'country' : '国家' ,
                        'province': '省份' ,
                        'avatarUrl': '头像图片地址',
                        'language' : '语言',
                        'gender'  : 性别(int) ,  (0是未知，1是男，2是女)
                        'nickName': '昵称',
                        'city' : '所在城市',  
                   }
        'signature' : '...',
        'encryptedData' : '被加密的数据',
        'errMsg': '错误信息', 
        'rawData' : '{...}',(好像和userInfo一样)
        'iv':'...'
    }

    #self.res_state 是一个如下的Json:
    {
        'code' : '...',
        'errMsg': '...'
    }
    '''
    def __init__(self):
        super(WxProtocol,self).__init__()
        self.start_operator = False     # 是否开始执行操作 （接收完用户信息时变为True
        self.res_info = ''
        self.res_state = ''
        self.session_key = ''   # 用于解得openid
        self.openid = ''        # 用户的唯一标识符
        self.Data = ''          # 解密后的数据 （多了一个openid 和water什么的
        self.carID = -1       # 该用户对哪一个车位进行占用申请
        self.balance = None     # 用户余额 
        self.cur_state = 0      # 用户当前状态

    # 对数据解密
    def decryptData(self):
        res = ''
        try:
            pc = WXBizDataCrypt(appid, self.session_key)
            res = pc.decrypt(self.res_info['encryptedData'],self.res_info['iv'])
        except Exception as err:
            print('error1.................')
            print(err)
        return res

    #当接收到数据的时候，会调用此函数
    def onMessage(self,data,isBinary):
        #send back what the server received
        #self.sendMessage(data,isBinary)
        if not isBinary :   # isBinary==False <=> bytes string
            data = data.decode('utf-8')

        # '$$'是结束标识符      
        if ( data=='$$' ):
            self.transport.loseConnection()

        #=============接收用户信息数据(建立连接)——res_Info和res_state============
        if not self.start_operator :
            try:
                data = json.loads(data) # 接收到的是一个json字符串
                #是res_state 
                if (tuple(data.keys())[0] == 'code' or tuple(data.keys())[1]=='code'):
                    self.res_state = data
                    #使用它来获取session_key
                    param['js_code'] = self.res_state['code']
                    res = requests.post(url,data=param)
                    try:
                        text = json.loads(res.text)
                        self.session_key = text['session_key']
                        self.openid = text['openid']
                    except Exception as err:
                        print('error2.................')
                        print(err)
                #是res_Info
                else: 
                    self.res_info = data

            #=================数据接收完毕===========================
                #received finished
                if (self.res_state != '' and self.res_info !=''):
                    self.start_operator = True  # 下次开始就是操作了
                    self.user_info_received()   # 调用 当接收完数据时需要触发的函数 
                    
                
            except Exception as err:
                print('error3.................')
                print(err)
        else: 
            # 当已经接收完毕的时候，执行wx发来的请求操作
            operation, value = data.split(':')
            print(operation,value) # debug print=>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>操作和值

            # 操作一：================充值操作===========================
            if operation == 'addMoney':
                value = float(value)
                self.balance = self.balance + value
                print(self.balance)             #=>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>剩余金额
                if update_user_data(self.openid,'balance',self.balance):
                    print('充值成功！')
                else:
                    print('充值失败！')
                msg = {}
                msg['balance'] = self.balance
                msg['header'] = 'balance'
                #发送给微信一个Json字符串，表示充值信息
                self.sendMessage(json.dumps(msg).encode())
            # 操作二：=============预订车位操作============================
            elif operation == 'carID':
                value = int(value)
                if self.balance >= 0 :
                    if eval(search_from_ps_db(value,'occupied')) == True: # 已经被占
                        # 看看是不是这个用户占的
                        if value == search_ucs_openId_to_carID(self.openid,'carID'):
                            #是这个用户占的
                            self.carID = value
                        else:
                            #不是这个用户占的
                            self.carID = -1
                    else:
                        #-------没有被占, 说明可以预订！-----------
                        self.carID = value
                        
                        #-------是否存在僵尸用户(扫了码不停车)------
                        pre_openid = search_ucs_carID_to_openId(self.carID,'openId')
                        if pre_openid : # 存在
                            self.delete_ghost_user()  # 删除僵尸用户
                        
                        # 微信端避免了同一用户多次扫码情况...
                        
                        #---------空车位被占，数据更新操作------------
                        self.cur_state = 1  # 状态更新为1 => 下了单但没停车

                else:# 余额不足
                    self.carID = -2

                #****建立映射关系*****
                if self.carID>0:
                    carID_to_Wx[self.carID] = self
                #*******************
    
                #===============给wx发送carID=================
                msgs = {}
                msgs['carID'] = self.carID
                msgs['header'] = 'carID'
                self.sendMessage(json.dumps(msgs).encode())
                #    预订一个车位
                self.reserve_parking_space() # 预订一个车位
        
            # 操作三：================询问当前时间=======================
            elif operation == 'askTime':
                start_t = search_from_user_db(self.openid,'start_time')
                # 不是'-'并且不是None
                if start_t != '-' and start_t :
                    last_t = time_tool.time_subtract(start_t, time_tool.get_Current_Time() )
                    msg = {}
                    msg['header'] = 'last_time'
                    msg['last_time'] = last_t
                    msg = json.dumps(msg)
                    self.sendMessage(msg.encode())
                    print('last_time信息发送成功...')

            # 操作四：================历史订单========================
            elif operation == 'askOrder':
                result = get_history_orders(self.openid)
                if result:
                    res = {}
                    res['header'] = 'his_order'
                    res['len'] = len(result)
                    order_list = ['start_time','stop_time','cost','last_time']
                    cnt = 1
                    for e in result:
                        #print('e:',e)
                        #print(type(e))
                        #print('order:',order_list)
                        assert len(e)==len(order_list)
                        elem = {}
                        for k,v in zip(order_list,e):
                            elem[k] = v
                        res[cnt] = elem
                        cnt = cnt + 1
                    print(res)
                    res = json.dumps(res)
                    self.sendMessage(res.encode())
                    print('历史订单发送成功!')
                else:
                    print('没有用户信息')


    # 删除掉僵尸用户(就是扫了码不停车然后走掉了)
    # 注意把用户状态也改了
    def delete_ghost_user(self):
        pass

    # 预订某一个车位
    def reserve_parking_space(self):
        if (self.carID < 0):
            return 
        #==================状态更新===================
        self.cur_state = 1  # 下了单但未停车
        update_parking_data(self.carID, 'openning',True)    # 车位可用
        insert_ucs_data(self.openid,self.carID)             # 建立映射关系
        update_user_data(self.openid,'cur_state',self.cur_state) # 状态变为预订没停车
        #============================================

    # 给微信发送数据库的用户信息
    def send_user_info(self):
        res_to_wx = get_user_info_from_db(self.openid)
        #print(res_to_wx)  #               >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>发送给wx的信息 
        res_to_wx = json.dumps(res_to_wx)
        self.sendMessage(res_to_wx.encode()) #这里传的不是bytes字符串
        print('users\' information send to wx successfully...')

    # res_info和res_state都接收完毕之后的操作 
    # 主要进行新用户的初始化 和 老用户的更新
    def user_info_received(self):
        #print(self.res_info)
        #print(self.res_state)
        self.Data = self.decryptData()  #decrypt data
        #如果是新用户
        if not query_user_existed(self.Data['openId']) :
            # 用户不存在
            # 新用户初始化
            self.cur_state = 0
            self.balance = 0.0
            if insert_user_data(self.Data,self.balance):
                print('user_Info insert successfully!')
            else:
                print('user_Info insert failed!')
        else:
            # 用户已存在
            # 老用户更新
            self.cur_state = search_from_user_db(self.openid,'cur_state')
            self.balance = search_from_user_db(self.openid,'balance')
            for key in self.res_info['userInfo']:
                if not update_user_data(self.Data['openId'] , key, self.res_info['userInfo'][key] ) :
                    print('update failed!')
            # 上次连接状态
            # cur_state => 0代表历史已完成订单和无状态 ，
            #              1代表下了订单但未停车， 
            #              2代表正在停车 ,
            #              3代表订单已完成，但消息未发送给wx端
            print('cur_state =>',self.cur_state) 
            self.send_user_info()       # 发给微信数据库里的用户信息

            if self.cur_state == 3:
                self.send_order_msg() 

                
    # 发送上次完成却没看到的订单信息++++ 记得改变用户状态state
    def send_order_msg(self):
        res = get_one_order_from_db(self.openid)
        res['header'] = 'timer_stop'
        res['balance'] = search_from_user_db(self.openid,'balance')# 零钱
        time.sleep(2)
        res = json.dumps(res)
        self.sendMessage(res.encode())
        update_user_data(self.openid,'cur_state',0)
        update_all_finished_order(self.openid)
        print('历史未发送订单发送成功...')

    def onConnect(self,request):
        print('client from %s'% request.peer)

    def onOpen(self):
        print('shake hand with %s succseefully .' % self.transport.getPeer())

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

# 和停车位的连接协议
class ArmProtocol(po.Protocol):
    def __init__(self):
        self.carID = -1             # 停车位号
        self.openning = False       # 是否允许被占用
        self.occupied = False       # 是否被占用
        self.start_time = ''      # 开始计时的时刻
        
    # 将数据库里的信息装填进来
    def Fill(self,carID):
        self.carID = carID
        self.openning = eval(search_from_ps_db(carID,'openning'))
        self.occupied = eval(search_from_ps_db(carID,'occupied'))

    # 消费费用的计算方法
    def cal_Cost(self,sec):
        return sec

    # 不能从ucs里找到用户信息++++++++++
    def raise_error(self):
        print('没有从ucs中找到用户信息')

    #=====================车开走了=========================
    # 1.计算时间 2.给wx发送消息 3.更新状态
    def carLeave(self):
        #wx_user = carID_to_Wx[self.carID]
        openid = search_ucs_carID_to_openId(self.carID,'openId')  # 获取openid
        if openid is None:
            self.raise_error()
            return 

        #=====计算时间======
        stop_Time = time_tool.get_Current_Time()
        sec = time_tool.time_subtract(self.start_time, stop_Time) # 获取持续时间
        cost_money = self.cal_Cost(sec)    #根据持续时间计算费用
        #wx_user.balance = wx_user.balance - cost_money
        balance = search_from_user_db(openid,'balance')
        balance = balance - cost_money
        #==================

        #=====给wx发消息=====
        msg = {}
        msg['header'] = 'timer_stop'
        msg['cost'] = cost_money
        msg['last_time'] = sec
        msg['current_time'] = stop_Time
        msg['current_money'] = balance
        msg = json.dumps(msg)

        user_state = 0 # 订单完成
        try:
            print(carID_to_Wx[self.carID].Data['userInfo']['nickName'],'还活着')
            carID_to_Wx[self.carID].sendMessage(msg.encode())
            print('%d号车位已空...' % self.carID)
        except Exception as err:
            # ++++++++++++++++和用户的连接断开了++++++++++++++++
            user_state = 3 # 订单完成但没发数据
            print('和用户连接断开...发送订单完成信息失败')
            # ++++++++++++++++++存入数据库++++++++++++++++++++
            
            
        #==================

        #=====注意，更新状态的时候，记得改变用户的状态->cur_state+++++++
        #=====更新状态=======

        #-----order状态------
        update_orders_data(openid,self.start_time,'cur_state',user_state)
        update_user_data(openid,'cur_state',user_state)
        print('cur_state更新成功为',user_state)
        update_orders_data(openid,self.start_time,'stop_time',stop_Time)
        update_orders_data(openid,self.start_time,'last_time',sec)
        update_orders_data(openid,self.start_time,'cost',cost_money)
        #-------------------

        a=update_user_data(openid, 'balance',balance) #更新余额
        b=delete_ucs_data(openid) # 删除user to carspace 的映射关系
        c=update_user_data(openid , 'start_time', '-') # 用户开始时间为'-'，说明未使用
        d=update_parking_data(self.carID,'start_time','-') # 车位开始时间变为'-'
        e=update_parking_data(self.carID,'openning',False) # 关闭可用状态
        f=update_parking_data(self.carID,'occupied',False) # 车位变为空
        #print(a,b,c,d,e,f)   #  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>情况
        #==================

    #====================车开来了=============================
    # 若合法： 1.开始计时 2.给微信发消息 3.更新状态
    # 若非法： 给当地管理员发送预警
    def carCome(self):
        if self.openning :
            openid = search_ucs_carID_to_openId(self.carID,'openId')
            if openid is None:
                self.raise_error()
                return 

            #========开始计时=======
            self.start_time = time_tool.get_Current_Time()
            #====================== 

            #========给wx发消息======
            msg = {}
            msg['header'] = 'timer_start'
            msg['time'] = self.start_time
            msg = json.dumps(msg)
            try:
                print(carID_to_Wx[self.carID].Data['userInfo']['nickName'],'还活着')
                carID_to_Wx[self.carID].sendMessage(msg.encode())
                carID_to_Wx[self.carID].cur_state = 2
                print('%d号车位被占...' % self.carID )
            except Exception as err:
                print('和wx用户连接断开...')
                #+++++++++和微信的连接断开了+++++++++++
                pass
                #+++++++++++++++++++++++++++++++++++
                
            #=======================

            # 注意。 记得更新用户的状态信息-> cur_state++++++++
            #=======更新状态========
            order_data = self.get_order_json(openid) # 获取一个order_json数据
            a = insert_orders_data(order_data)    # 在订单中插入一条
            print(order_data)
            print(a)
            update_user_data(openid,'cur_state',2) # 正在停车状态
            update_parking_data(self.carID,'start_time', self.start_time) # 更新车位数据库的开始时间
            update_user_data(openid, 'start_time', self.start_time)  # 更新用户计时的开始时间
            update_parking_data(self.carID,'occupied',True) # 车位被占
            #======================
        else:
            print('有人非法占领车位！！！！！！！！！！！！！！！！！！！')

    def get_order_json(self,openid):
        res = {}
        res['start_time'] = self.start_time
        res['stop_time'] = '-'
        res['cur_state'] = 2
        res['openId'] = openid
        res['cost'] = -1
        res['last_time'] = -1
        return res

    # 当接收到数据的时候，会调用这个函数
    def dataReceived(self,data):
        #self.transport.write(data)
        #data = data.decode('utf-8')
        #print('pre:',data)
        #print(type(data))
        data = armDecry(data)
        #print(data)
        #print(type(data))
        ps_state, carID = data.split()
        carID = int(carID)
        self.Fill(carID)
        #print(tuple(carID_to_Wx.keys()))            >>>>>>>>>>>>>>>>>>>>>>>>>>类型输出
        #print(carID)                               >>>>>>>>>>>>>>>>>>>>>>>>>>>类型输出
        # 车位为空-> 车走了
        if ps_state == '0':
            self.carLeave()  
        # 车位被占-> 车来了
        elif ps_state == '1':
            self.carCome()
    #         
    def connectionMade(self):
        print('connecting from %s' % self.transport.getPeer())

class ArmServerFactory(po.ServerFactory):

    protocol = ArmProtocol

    def __init__(self):
        pass
