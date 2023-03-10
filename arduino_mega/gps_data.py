import serial
import socket


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'localhost'
port = 5000

s.bind((host, port))
s.listen(1)
conn, addr = s.accept()

ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)  # /dev/ttyACM0에서 9600으로 시리얼 포트 열기.
count = 1
f= open("/home/jetson/Desktop/project/bike-lane-pro/jetson/opencv_lane_detect/gps_data.txt",'w') # 파일 만들고 쓰기
f.write("sequence,time,latitude,longitude\n")
while True:
    r_data = conn.recv(1024).decode()
    rx = ser.readline().decode()
    data_type = rx.split(']')
    if(data_type[0] == "[GPS"):
        print(count, data_type[-1])
        f.write(str(count) + ',')
        f.write(data_type[-1])
        count = count + 1
    
    num = int(r_data)
    if(num == 10):break
    
    
f.close() #파일 닫기
ser.close()   # 시리얼 통신 종료
