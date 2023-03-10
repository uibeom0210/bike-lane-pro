import serial
import sys
import subprocess

ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)  # /dev/ttyACM0에서 9600으로 시리얼 포트 열기.
count = 1
f= open("/home/lee/gyu/gps_data.txt",'w') # 파일 만들고 쓰기
f.write("sequence,time,latitude,longitude\n")
while True:
    rx = ser.readline().decode()
    data_type = rx.split(']')
    if(data_type[0] == "[GPS"):
        print(count, data_type[-1])
        f.write(str(count) + ',')
        f.write(data_type[-1])
        count = count + 1
    result = subprocess.check_output(['python', 'script1.py'])    
    if(result == 10):
        break
f.close() #파일 닫기
ser.close()   # 시리얼 통신 종료