import asyncio # 비동기화 통신을 위한 라이브러리
import bleak # bleak 라이브러리
from bleak import BleakClient

address = "2D:6F:AB:3C:F5:F4"
#address = "8E:09:AB:27:76:D0"
#address = "63:C2:8F:29:36:89"

notity_charcteristic_uuid_accel = "741c12b9-e13c-4992-8a5e-fce46dec0bff"
notity_charcteristic_uuid_gyro = "baad41b2-f12e-4322-9ba6-22cd9ce09832"
notity_charcteristic_uuid_mag = "5748a25d-1834-4c68-a49b-81bf3aeb2e50"

accel_ble_data = []
gyro_ble_data = []
mag_ble_data = []

accel_ble_string = []
gyro_ble_string = []
mag_ble_string = []

IMU_data = ""

f= open("IMU_data.csv",'w')
f.write("sequenece,AccelX,AccelY,AccelZ,GyroX,GyroY,GyroZ,MagnX,MagnY,MagnZ\n")

def notify_callback_accel(sender: int, data: bytearray):
    # print(data)
    accel_ble_data.append(data)
    
def notify_callback_gyro(sender: int, data: bytearray):
    gyro_ble_data.append(data)

def notify_callback_mag(sender: int, data: bytearray):
    mag_ble_data.append(data)

async def run(address):
    async with BleakClient(address) as client:
        print('connected') # 연결을 성공함
        services = await client.get_services()
        for service in services:
            for characteristic in service.characteristics:
                if characteristic.uuid == notity_charcteristic_uuid_accel:
                    if 'notify' in characteristic.properties:
                        await client.start_notify(characteristic, notify_callback_accel)
                if characteristic.uuid == notity_charcteristic_uuid_gyro:
                    if 'notify' in characteristic.properties:
                        await client.start_notify(characteristic, notify_callback_gyro)
                if characteristic.uuid == notity_charcteristic_uuid_mag:
                    if 'notify' in characteristic.properties:
                        await client.start_notify(characteristic, notify_callback_mag)

        # client 가 연결된 상태라면
        if client.is_connected:
            # 10초간 대기
            await asyncio.sleep(30)
            print('try to deactivate notify.')
            # 활성시켰던 notify를 중지 시킨다.
            await client.stop_notify(notity_charcteristic_uuid_accel)
            await client.stop_notify(notity_charcteristic_uuid_gyro)
            await client.stop_notify(notity_charcteristic_uuid_mag)
    print('disconnect')

#################################################################
loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))

# str_data = str(data, 'utf-8')
length = len(accel_ble_data)
for index in range(length):
    str_data = str(accel_ble_data[index], 'utf-8')
    accel_ble_string.append(str_data)

length = len(gyro_ble_data)
for index in range(length):
    str_data = str(gyro_ble_data[index], 'utf-8')
    gyro_ble_string.append(str_data)

length = len(mag_ble_data)
for index in range(length):
    str_data = str(mag_ble_data[index], 'utf-8')
    mag_ble_string.append(str_data)

length = min(len(accel_ble_data), len(gyro_ble_data))
length = min(length, len(mag_ble_data))
for index in range(length):
    IMU_data = str(index) + ',' + accel_ble_string[index] + gyro_ble_string[index] + mag_ble_string[index] + '\n'
    # print(IMU_data)
    f.write(IMU_data)
f.close()

print('done')
