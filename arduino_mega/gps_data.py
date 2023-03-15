import serial
import datetime

ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)  # /dev/ttyACM0에서 9600으로 시리얼 포트 열기.
count = 1

now = datetime.datetime.now()
target_time = now + datetime.timedelta(minutes=5)
f= open(f"/home/pi/gps_data{now.hour}-{now.minute}-{now.second}.csv",'w') # 파일 만들고 쓰기
f.write("sequence,time,latitude,longitude,speed\n")
while True:
    now = datetime.datetime.now()
    rx = ser.readline().decode()
    data_type = rx.split(']')
    if(data_type[0] == "[GPS"):
        print(count, data_type[-1])
        f.write(str(count) + ',')
        f.write(data_type[-1])
        count = count + 1
    if now >= target_time:
        f.close()
        f= open(f"/home/pi/gps_data{now.hour}-{now.minute}-{now.second}.csv",'w')
        f.write("sequence,time,latitude,longitude,speed\n")        
        target_time = now + datetime.timedelta(minutes=5)
    
     #if 라즈베리 젯슨 통신 값    
f.close() #파일 닫기
ser.close()   # 시리얼 통신 종료

