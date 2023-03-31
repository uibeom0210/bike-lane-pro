import asyncio
from datetime import datetime
# import bleak
from bleak import BleakClient
from bleak import BleakError
import os

IMU_SENSOR_2D = 0
IMU_SENSOR_2F = 1

if IMU_SENSOR_2D == 1:
    address = "2D:6F:AB:3C:F5:F4" #_IMU_SENSOR_2D_
    notity_charcteristic_uuid_accel = "741c12b9-e13c-4992-8a5e-fce46dec0bff"
    # notity_charcteristic_uuid_gyro = "baad41b2-f12e-4322-9ba6-22cd9ce09832"
    # notity_charcteristic_uuid_mag = "5748a25d-1834-4c68-a49b-81bf3aeb2e50"
if IMU_SENSOR_2F == 1:
    address = "2F:92:31:56:F4:C7"
    notity_charcteristic_uuid_accel = "f3f014e9-e1c9-4ab4-9542-44ff558ceb95"
    # notity_charcteristic_uuid_gyro = "3e03fe4b-692f-4f66-8ec2-9efdf7646357"
    # notity_charcteristic_uuid_mag = "e8ea1646-a319-40bb-9872-cf6370174819"

file_name = ""

count = 0
sequence = 0
cur_time = 0
pre_time = 0

def makeDataFile():
    global file_name
    time = datetime.now()
    file_name = f"/home/pi/Desktop/IMU/IMU_{time.hour:02d}{time.minute:02d}{time.second:02d}.csv"
    with open(file_name, "w") as f:
        f.write("sequence,AccelX,AccelY,AccelZ,time\n")

def notify_callback_accel(sender: int, data: bytearray):
    global cur_time
    global pre_time
    global sequence
    
    str_data = str(data, 'utf-8')
    now = datetime.now()
    cur_time = now.minute
    imu_data = f"{sequence},{str_data}{now.hour:02d}{now.minute:02d}{now.second:02d}\n"
    print(imu_data)
    sequence += 1
    with open(file_name, "a") as f:
        f.write(imu_data)

async def run(address):
    global cur_time
    global pre_time
    global sequence
    global count

    cnt = 0
    
    while True:
        client = BleakClient(address, timeout=10) # timeout 값을 10으로 수정
        if client.is_connected:
            # BLE 기기와의 연결 상태를 확인합니다.
            pass
        else:
            # BLE 기기와의 연결이 끊어졌을 때 다시 연결을 시도합니다.
            try: 
                print("Trying to connect to device...")
                await client.connect()
                # BLE 기기와의 연결이 성공하면 데이터 수집을 시작합니다. 
                print("Connected to device successfully!")
                now = datetime.now()
                pre_time = now.minute
                makeDataFile()
                break
            except:
                # BLE 기기와의 연결이 실패하면 잠시 대기한 후 다시 시도합니다.
                print("Failed to connect to device")
                await asyncio.sleep(1)
                continue
    while True:
        try:
            services = client.services
            for service in services:
                for characteristic in service.characteristics:
                    if characteristic.uuid == notity_charcteristic_uuid_accel:
                        if 'notify' in characteristic.properties:
                            await client.start_notify(characteristic, notify_callback_accel)
                    if cur_time - pre_time >= 1:
                        print("makefile : ",cur_time)
                        sequence = 0
                        count += 1
                        print(f"IMU file count : {count}")
                        pre_time = cur_time
                        print(f'\t\t\t\t\tnew_pre_time : {pre_time}')
                        makeDataFile()
        except Exception as e:
            print(e)
            cnt += 1
            if(cnt >= 50):
                await client.stop_notify(notity_charcteristic_uuid_accel)
                await client.disconnect()
                break
            continue
        else:
            if client.is_connected:
                if count >= 5:
                    print('try to deactivate notify.')
                    await client.stop_notify(notity_charcteristic_uuid_accel)
                    await client.disconnect()
                    count = 0
                    break
                else:
                    pass

asyncio.run(run(address))
