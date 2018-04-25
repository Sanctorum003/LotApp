import time

'''
# 格式化时间 => 时间戳
# a是格式化时间
ta = time.mktime(time.strptime(a,"%Y-%m-%d %H:%M:%S"))
'''

# 标准格式时间为：'2017-12-10 09:56:06' <str>

def errPrint():
    print('格式错误...标准格式为: "2017-12-10 09:56:06"')
    print('您可以使用语句:  time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))')
    
# 两个标准格式时间相减，返回时间差（单位为秒）
def time_subtract(t1,t2):
    if ( t1=='-' or t2=='-' ):
        return -1
    sec1 = time.mktime(time.strptime(t1,"%Y-%m-%d %H:%M:%S"))
    sec2 = time.mktime(time.strptime(t2,"%Y-%m-%d %H:%M:%S"))
    total_sec = (sec2-sec1)
    return total_sec

# 获取当前标准格式时间
def get_Current_Time():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))