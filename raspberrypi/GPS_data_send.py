import serial
import datetime

ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1) #communication
count = 0
file_count = 0
file_name = ''
now = datetime.datetime.now()
target_time = now + datetime.timedelta(minutes=2)
file_name = f"/home/pi/Desktop/GPS/GPS_{now.hour:02d}{now.minute:02d}{now.second:02d}.csv" #used datetime
f= open(file_name,'w')
f.write("sequence,datetime,gpstime,latitude,longitude,speed\n") #Save 5 value
f.close()

while True:
    rx = ser.readline().decode()
    data_type = rx.split(']') #parsing
    if(data_type[0] == "[GPS"):
        f= open(file_name,'a')
        f.write(f"{count},{now.hour:02d}{now.minute:02d}{now.second:02d},")
        f.write(data_type[-1])
        f.close()
        count = count + 1
    if now >= target_time: #if 2minute later
        file_count += 1
        count = 0
        if file_count == 10: #if file_count 10 finish
            break
        file_name = f"/home/pi/Desktop/GPS/GPS_{now.hour:02d}{now.minute:02d}{now.second:02d}.csv" #repeat
        f= open(file_name,'w')
        f.write("sequence,datetime,gpstime,latitude,longitude,speed\n")
        f.close()
        target_time = now + datetime.timedelta(minutes=2)

ser.close()
