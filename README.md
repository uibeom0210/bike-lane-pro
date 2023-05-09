# 프로젝트 개요

![bike_lane_pro_system](https://github.com/uibeom0210/bike-lane-pro/assets/26503925/94eea2c7-0309-4602-bde9-74e4ff6c6f22)

본 시스템은 자전거에 카메라와 가속도 센서, GPS 센서를 부착하여 여러가지 데이터를 수집했습니다. 이렇게 수집한 데이터는 젯슨과 파이를 통해 실시간으로 분석되고 처리됩니다. 카메라를 통해 촬영한 영상은 OpenCV와 PyTorch, Yolov5 알고리즘을 통해 도로 노면상의 pothole을 실시간으로 감지하여, 이를 파이에 전송합니다. 가속도 센서는 자전거 뒷바퀴에 부착되어 바퀴 회전 시마다 주기성을 가지는 파형을 생성하며, 이를 BLE 통신을 통해 파이에 전송합니다. GPS 센서는 일정 시간마다 자전거가 이동한 위치를 추적하고 해당 위치의 좌표를 수집합니다. 이렇게 수집한 데이터를 활용하여 현재 pothole이 존재하는 자전거 도로 위치를 지도상에 맵핑합니다. 이 과정을 실시간으로 진행되도록 하였습니다.

# 개발 환경

![개발환경](https://github.com/uibeom0210/bike-lane-pro/assets/26503925/81f77d54-8694-4db0-a2fb-0dd63f90d0be)

본 프로젝트에서는 다양한 보드들을 사용하여 개발을 진행하였다. Arduino Mega(이하 메가)와 Arduino nano 33 BLE(이하 나노), Jetson Nano Board(이하 젯슨), Raspberry Pi(이하 파이)를 사용하였으며, Arduino 보드 개발은 C/C++를 사용하였습니다. 파이와의 소통을 위해서는 Raspbian 환경이 이용되었습니다.

TinyGPS.h 라이브러리는 GPS 센서가 받아오는 값을 필요한 정보로 구분하고, 지도가 인식할 수 있는 값으로 변환하는 함수를 제공합니다. LSM9DS1.h 라이브러리는 가속도 센서의 값을 받아 원하는 형태로 수정하기 위해 사용되었습니다. Arduino IDE와 VScode를 주로 사용하여 개발을 진행하였으며, 젯슨과 파이를 개발할 때는 주로 파이썬 언어를 사용하였습니다. C 언어는 HTML 및 OpenCV를 사용할 때 활용되었습니다.

젯슨과 파이의 차이점은 젯슨이 영상 처리 및 객체 인식에 Pytorch와 OpenCV를 사용하는 반면, 파이는 서버의 역할로 주로 통신, 데이터 수신 및 저장을 담당하였습니다. 젯슨은 코랩을 통해 데이터 학습을 진행하고, Tensor Board를 사용하여 학습한 데이터의 정확도를 확인할 수 있었습니다. VScode를 주로 사용하여 개발 환경을 구성하였습니다.

# 개발 과정

## IMU, GPS 센서로부터 데이터 수집

<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/04ab5ea9-5187-4826-8f97-46f2d9f2d2b1"  width="40%" height="50%"/> <img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/ee2a1d81-04aa-4ebf-9130-74266bb15663"  width="40%"/>

수집 프로그램을 실행할 때, Raspberry Pi와 BLE 장치 간의 연결이 즉각적으로 이루어지지 않는 어려움이 있었습니다. 이를 해결하기 위해 연결이 성공할 때까지 반복적으로 연결을 시도하는 코드를 추가하였습니다. 또한, 프로그램이 시작되면 1분마다 데이터를 송신하도록 설정하였습니다. 프로그램이 종료될 때는 연결을 끊어주어 중복 연결이나 프로그램 중복 실행이 발생하지 않도록 조치하였습니다. 이후, 센서가 보내는 데이터가 Notify 형식인지 확인하고 데이터를 수신하기 시작합니다. 수신한 데이터는 팀 프로토콜에 따른 CSV 형식으로 전송하며, Raspberry Pi는 이 데이터를 CSV 파일로 저장한 후 Jetson Nano 보드에게 scp 프로토콜을 사용하여 전송합니다. |  |

<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/fe37acf0-c390-41b9-862c-63fde59e8526"  width="40%" height="50%"/> <img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/20db3b90-466f-4533-9dc7-33a336264603"  width="40%"/>

Arduino Mega(이하 메가)와 GPS 센서가 통신을 완료하여 GPS 데이터 값을 받아오면, 메가에서 파이로 다시 한 번 GPS 데이터 값을 송신합니다. 파이에서는 수신된 데이터를 필요에 맞게 분할하여 CSV 파일로 저장합니다. 이때, 파이에 사용된 파이썬 코드에서는 datetime 라이브러리를 활용하여 파일명에 시간을 기록하여 팀 프로토콜에 맞춰 다른 데이터들과 비교가 용이하도록 설정하였습니다. 또한, CSV 파일에는 datetime 시간을 같이 기록하여 GPS 값으로 들어온 시간과 비교하여 값에 이상이 있는지 확인하는 추가적인 검증을 수행합니다. 데이터는 번호, 날짜 및 시간, 위도, 경도, 속도 순으로 기록되며, 사용자가 원하는 시간대에 따라 파일을 새로 생성하여 저장됩니다. 이를 통해 데이터의 순서와 형식이 일관성을 유지하며, 파일명에 포함된 datetime 정보를 활용하여 데이터의 시간 관련 정보를 체크 할 수 있습니다. |  |

## Camera로부터 영상 데이터 수집과 처리

| <img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/512b9db1-e5cc-4b50-9865-26a5cb2a95a5" /> | 카메라를 도로 진행 방향으로 일정 높이만큼 높여서 고정하고 촬영하였습니다. 이렇게 함으로써 초기 영상이 차선 진행 방향에 대해 일정한 각도로 기울어져 있어 차선을 인식하는 것이 용이해졌습니다. 그 다음으로, 관심 영역(Region of Interest, ROI)을 설정하여 사각형의 좌표를 입력하고, 사각형 안쪽 영역을 잘라서 연산을 수행하였습니다. 이를 통해 전체 이미지에 대한 연산을 수행하지 않고, 처리 속도와 메모리 사용량을 최적화할 수 있었습니다. |
| --- | --- |

## pothole 검출 전체 알고리즘 구현

<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/931f136d-7620-46db-a897-9195a7b7c159"  width="30%" height="50%"/> <img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/462f5c23-b922-48de-9721-698abb420996"  width="60%" height="50%"/>

가속도 센서 데이터를 분석한 결과, 자전거 바퀴가 한 바퀴를 돌 때마다 가속도 센서가 약 -10000부터 10000까지의 값을 주기적으로 가진다는 것을 확인하였습니다. 또한 자전거의 속도가 빠를수록 도로 위의 pothole에서 가속도 센서의 값이 크게 측정되는 것을 발견하였습니다. 따라서 자전거의 속도를 계산하는 것이 필수적이었습니다. 측정 기간은 1분이며, 데이터는 1초에 약 50~60개 저장되며 손실을 고려하면, 파일 하나에는 약 3,000개 이상의 데이터가 저장됩니다. 이 데이터를 일정 간격으로 분할하여 작은 단위로 Segmentation하고, 각 단위의 평균값을 구하여 Noise Smoothing을 진행합니다. 먼저 바퀴 둘레와 샘플링 주파수를 사용하여 한 파형의 단위 속도를 계산한 다음, 일정 구간마다 몇 번의 파동이 발생하는지 계산해야 합니다. 이를 위해 센서값이 구간 전체 평균을 기준으로 얼마나 교차하는지(count)를 계산합니다. 마지막으로, count 수와 단위 속도를 곱하여 자전거의 속도를 도출합니다.

<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/0946c28a-fe72-4b03-8387-0c7fa3856077"/>

가속도 센서 분석 툴에서 도출한 결과를 바탕으로, Pothole에 대한 Threshold 값을 15000 이상으로 설정하였습니다. 이 Threshold 값을 비교할 기준 값을 생성하였는데, 이 값은 자전거의 속도가 빠를수록 Threshold를 넘기기 어렵게 조절되었습니다. 만약 충격 값이 감지되면, 해당 시점의 시간 정보를 추출하고 GPS 데이터의 시간 정보와 매칭합니다.

## 데이터셋 생성과 학습

### 데이터셋 전처리

<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/c2c85b20-ad1e-49d4-8e06-6c81f2831927" />

객체 인식으로 희망하는 객체로는 pothole, manhole, bike marking 3가지를 선정했다. 데이터 베이스 구성 대부분은 Roboflow를 통해서 진행됐다. Robofow에서 pothole, manhole 데이터 셋은 이미 많이 구성되어 있어 주로 다운을 받아 진행하였고 bike marking 데이터는 찾을 수 없어 직접 촬영 및 데이터 셋을 모아 학습을 진행하였다.

### 데이터 학습

데이터 학습 단계는 Colab을 통해 진행되며 데이터 학습에 필요한 패키지를 다운로드 하고 import를 진행한다. 데이터 셋과 안에 있는 yaml 파일의 경로를 설정해주고 만든 데이터 셋의 yaml 파일을 코드를 통해 “test, valid, train 그룹이 잘 나누어졌는지”, “클래스가 설정한대로 잘 설정되었는지” 등을 확인한다. 잘 학습된 게 확인되면 Yolo5를 통해 데이터 셋을 학습시킨다.

학습을 시키기 전 학습 설정을 줄 수 있다. 이때 가장 중요한 설정 값은 epoch 값이다. epoch은 훈련 데이터 셋에 포함된 모든 데이터들이 한 번씩 모델을 통과한 횟수로, 모든 학습 데이터 셋을 학습하는 횟수를 말한다. epoch이 높을수록 다양한 무작위 가중치가 학습되다 보니 적합한 파라미터를 찾을 확률이 올라가지만 지나치게 값을 높이면 학습 데이터 셋에 과 적합하게 되어 다른 데이터에 대해서 제대로 인식하지 못하는 문제가 발생할 수 있다.

<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/d083b15c-1f20-440f-8ef0-fc17347cdf85" width="55%" height="50%" />

<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/19bb492f-dbff-47d8-86b2-8bd8add7f370"  width="55%" height="50%"/> <img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/220cdfc0-d757-4e6f-b484-109f36739fa9"  width="44%" height="50%"/>

## 시각화

<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/634e555b-3b48-4de8-9143-69e1fb311acf"  width="40%" height="50%"/> <img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/16b3a6b2-ffac-4c72-971e-e0795e282f32"  width="50%" height="50%"/>

Pothole Capture 사진과 IMU를 통해 탐색한 Pothole의 위치를 GPS 좌표와 매칭하여 하나의 CSV 파일에 누적시킵니다. 지도에 맵핑할 때, 서로 다른 시간에 동일한 장소를 주행하면 같은 Pothole이 중복으로 검출되어 마크가 중복으로 발생할 수 있습니다. 이를 방지하기 위해 CSV 파일에 데이터를 누적시킬 때, 일정 거리 안에 생성된 새로운 좌표라면 파일에 추가하지 않도록 조치하였습니다. 다음은 GPS 좌표와 매칭된 Pothole 검출 위치로, 검출 시간과 좌표(위도, 경도), 그리고 Pothole의 심각도에 대한 정보가 제공됩니다.

<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/ac7a6bc7-5b5f-4df2-949a-a4d69c310af9"  width="40%" height="50%"/>
<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/d083b15c-1f20-440f-8ef0-fc17347cdf85" width="40%" height="50%"/>

지도 시각화 시연을 통해 자전거가 이동함에 따라 Pothole 검출 횟수가 증가하고, 이에 따라 지도에 맵핑되는 Pothole 마크들이 늘어나는 모습을 확인할 수 있습니다.

<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/9ea687e9-11e5-479c-93a9-136ec599930a"  width="40%" height="50%"/>
<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/f0a7761b-2eae-4dba-a104-ce853ee68d4e"  width="40%" height="50%"/>

검출한 Pothole 위치에는 Pothole을 캡쳐한 사진 자료가 추가됩니다. 이를 통해 각 Pothole의 위치를 더 명확하게 확인할 수 있습니다.

## 하드웨어 제작

<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/f6096f3b-e188-4846-8e78-d67c73480d6c"  width="30%"/>
<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/4513e5b8-b604-4a30-b244-2b4bedc1ade8"  width="30%"/>
<img src="https://github.com/uibeom0210/bike-lane-pro/assets/26503925/c76e1bcd-5b02-407c-924c-25523590035c"  width="30%"/>

나노 보드는 자전거 휠에 부착하기 위해 가능한 작은 크기로 제작되었습니다. 또한 무선으로 사용하기 위해 충전형 리튬 배터리와 충전 모듈, 그리고 스위치가 연결되어 있습니다. 하드웨어 외부에는 젯슨 나노 보드의 상태를 확인할 수 있는 디스플레이, Arduino 보드, 그리고 GPS 센서가 장착되어 있습니다. GPS 안테나는 외부에 위치하여 데이터를 수신할 수 있도록 설치되었습니다. 또한, LCD 디스플레이는 프로젝트를 실외에서 실험할 때 젯슨 나노 보드를 모니터링하기 위해 설치되었습니다.

# 개선 및 발전 방향

Pothole 감지 뿐만 아니라 전체 도로의 노면 상태를 레벨 별로 구분하여 연속적인 데이터 값을 만들 수 있다면, 도로를 전체적으로 유지하고 보수하는 데에 도움이 될 것으로 예상됩니다. 또한, 자전거 도로에는 Pothole 이외에도 쓰레기 무단투기로 인한 환경 문제 등 다양한 문제가 존재합니다. 현재는 자전거 도로의 파손만을 확인하고 있지만, 추가 교육을 통해 인식되는 객체가 늘어난다면 쓰레기 양에 따른 청결 상태, 도보 및 차도 도로 상태, 도시 치안 등의 문제를 모델 학습을 통해 조기에 발견하여 해결할 수 있다면, 좀 더 발전된 자전거 도로 관리 시스템을 구현할 수 있을 것으로 생각됩니다.