import asyncio
from bleak import BleakScanner

'''
 장치가 검색되면 호출되는 콜백 함수
 device: 장치 정보(bleak.backends.device.BLEDevice)
 advertisement_data: 장치에서 송출하는 데이터
'''
def detection_callback(device, advertisement_data):
    # 장치 주소와 신호세기, 그리고 어드버타이징 데이터를 출력한다.
    print(device.address, "RSSI:", device.rssi, advertisement_data)

async def run():
    # 검색 클래스 생성
    scanner = BleakScanner()
    # 콜백 함수 등록
    scanner.register_detection_callback(detection_callback)
    # 검색 시작
    await scanner.start()
    # 5초간 대기 이때 검색된 장치들이 있다면 등록된 콜백함수가 호출된다.
    await asyncio.sleep(5.0)
    # 검색 중지
    await scanner.stop()
    # 지금까지 찾은 장치들 가져오기
    devices = await scanner.get_discovered_devices()
    # 지금까지 찾은 장치 리스트 출력
    for d in devices:
        print(d)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())