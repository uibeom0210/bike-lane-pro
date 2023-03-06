import asyncio # 비동기화 통신을 위한 라이브러리
# import bleak   # bleak 라이브러리
from bleak import BleakClient

address = "2D:6F:AB:3C:F5:F4"
# address = "8E:09:AB:27:76:D0"
# address = "63:C2:8F:29:36:89"
notity_charcteristic_uuid_x_level = "741c12b9-e13c-4992-8a5e-fce46dec0bff"
notity_charcteristic_uuid_y_level = "baad41b2-f12e-4322-9ba6-22cd9ce09832"
notity_charcteristic_uuid_z_level = "5748a25d-1834-4c68-a49b-81bf3aeb2e50"

# ble nano가 notify로 보낸 데이터를 받는 콜백함수
def notify_callback_x_level(sender: int, data: bytearray):
    print('sender: ', sender, 'x_data: ', data)

def notify_callback_y_level(sender: int, data: bytearray):
    print('sender: ', sender, 'y_data: ', data)

def notify_callback_z_level(sender: int, data: bytearray):
    print('sender: ', sender, 'z_data: ', data)

async def run(address):
    # BleakClient 클래스 생성 및 바로 연결 시작
    # timeout: 연결 제한 시간 5초가 넘어가면 더 이상 연결하지 말고 종료
    async with BleakClient(address, timeout=5.0) as client:
        print('connected') # 연결을 성공함
        # 연결된 BLE 장치의 서비스 요청
        services = await client.get_services()
        # 서비스들을 루프돌려 내부 캐릭터리스틱 정보 조회
        for service in services:
            # 각 서비스들에 있는 캐릭터리스틱을 루프 돌려 속성들 파악하기
            for characteristic in service.characteristics:
                # 캐릭터리스틱 UUID가 우리가 찾는 UUID인지 먼저 확인
                if characteristic.uuid == notity_charcteristic_uuid_x_level:
                    # 해당 캐릭터리스틱에 notify 속성이 있는지 확인
                    if 'notify' in characteristic.properties:
                        # notify 속성이 있다면 BLE 장치의 notify 속성을 
                        # 활성화 작업 후 notify_callback 함수 연결
                        # print('try to activate notify.')
                        await client.start_notify(characteristic, notify_callback_x_level)

                # if characteristic.uuid == notity_charcteristic_uuid_y_level:
                #     # 해당 캐릭터리스틱에 notify 속성이 있는지 확인
                #     if 'notify' in characteristic.properties:
                #         # notify 속성이 있다면 BLE 장치의 notify 속성을 
                #         # 활성화 작업 후 notify_callback 함수 연결
                #         # print('try to activate notify.')
                #         await client.start_notify(characteristic, notify_callback_y_level)
                        
                # if characteristic.uuid == notity_charcteristic_uuid_z_level:
                #     # 해당 캐릭터리스틱에 notify 속성이 있는지 확인
                #     if 'notify' in characteristic.properties:
                #         # notify 속성이 있다면 BLE 장치의 notify 속성을 
                #         # 활성화 작업 후 notify_callback 함수 연결
                #         # print('try to activate notify.')
                #         await client.start_notify(characteristic, notify_callback_z_level)

        # client 가 연결된 상태라면
        if client.is_connected:
            # 7초간 대기
            await asyncio.sleep(7)
            print('try to deactivate notify.')
            # 활성시켰던 notify를 중지 시킨다.
            await client.stop_notify(notity_charcteristic_uuid_x_level)
            # await client.stop_notify(notity_charcteristic_uuid_y_level)
            # await client.stop_notify(notity_charcteristic_uuid_z_level)
    print('disconnect')


loop = asyncio.get_event_loop()
loop.run_until_complete(run(address))
print('done')