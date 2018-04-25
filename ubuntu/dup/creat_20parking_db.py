# 自动生成20个车位 
from parkingspace_db_util import insert_parking_data

for i in range(1,21):
    insert_parking_data(i,False,False,"-")
