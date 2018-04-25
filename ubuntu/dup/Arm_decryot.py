def armDecry(bstr):
    start = 5
    end = start + bstr[4]
    # cs = 0
    # for i in range(0,end):
    #     cs = cs + bstr[i]
    # if (cs%256) != bstr[end]:
    #     return ''
    res = bstr[start:end]
    return res.decode('utf-8')

