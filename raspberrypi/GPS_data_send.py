import serial
import datetime

ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1) #serial commu
count = 0
file_count = 0
file_name = ''
pretime = datetime.datetime.now() #nowtime
file_name = f"/home/pi/Desktop/GPS/GPS_{now.hour:02d}{now.minute:02d}{now.second:02d}.csv" #used datetime
f= open(file_name,'w')
f.write("sequence,datetime,gpstime,latitude,longitude,speed\n") #data
f.close()

while True:
    cur_time = datetime.datetime.now()
    rx = ser.readline().decode()
    data_type = rx.split(']') #parsing
    if(data_type[0] == "[GPS"):
        f= open(file_name,'a')
        f.write(f"{count},{cur_time.hour:02d}{cur_time.minute:02d}{cur_time.second:02d},")
        f.write(data_type[-1])
        print(rx)
        f.close()
        count = count + 1
    if cur_time.minute - pre_time.minute >= 1: #if 1minute later
        file_count += 1
        print(f"gps file count : {file_count}")
        count = 0
        if file_count == 20: #if file_count 10 finish
            break
        file_name = f"/home/pi/Desktop/GPS/GPS_{cur_time.hour:02d}{cur_time.minute:02d}{cur_time.second:02d}.csv" #repeat
        f= open(file_name,'w')
        f.write("sequence,datetime,gpstime,latitude,longitude,speed\n")
        f.close()
        pre_time = cur_time
        # target_time = now + datetime.timedelta(minutes=2)

ser.close()
