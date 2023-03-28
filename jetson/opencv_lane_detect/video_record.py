import cv2
from datetime import datetime


try:
    video = cv2.VideoCapture(0, cv2.CAP_V4L2) # 비디오 캡쳐 객체 생성
    if not video.isOpened(): raise Exception("error") # 카메라 오픈 실패 시 에러 처리
    
    fps = video.get(cv2.CAP_PROP_FPS) # FPS 가져오기
    frame_cnt = 1 # 현재 프레임 카운트
    width = video.get(cv2.CAP_PROP_FRAME_WIDTH) # 비디오 프레임 가로 길이
    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT) # 비디오 프레임 세로 길이
    fourcc = cv2.VideoWriter_fourcc(*'XVID') # 영상 코덱 설정
    i=0 # 루프 종료용 변수
except Exception as e:
    print("Exception occurred:", e)

#영상 녹화 시작 및 루프 실행
pre_time = datetime.now() # 이전 녹화 시작 시간 초기화
pre_time_name = pre_time.strftime('%H%M%S') # 파일 이름에 사용될 시간 변수 초기화
while True:
    try:
        out = cv2.VideoWriter(f'/home/jetson/Desktop/CAM/CAM_{pre_time_name}.avi',fourcc,fps,(int(width),int(height))) # 녹화할 영상 파일 생성
        cnt = 0 # 현재 녹화된 프레임 카운트
        while(video.isOpened()): # 카메라가 열려있는 동안 루프 실행
            ret, frames = video.read() # 영상 프레임 읽기
            if not ret: break # 프레임 읽기 실패 시 루프 종료

            cv2.imshow('original',frames) # 원본 영상 화면 출력
            out.write(frames) # 영상 파일에 프레임 저장
            cur_time = datetime.now() # 현재 시간 저장

            if (cur_time.minute - pre_time.minute >= 2): # 녹화 시작 시간부터 2분이 지나면 새로운 파일 이름 생성
                pre_time = cur_time
                pre_time_name = pre_time.strftime('%H%M%S')
                i = i +1 # 루프 종료용 변수 값 증가
                break 

            if cv2.waitKey(1)&0xff==ord('q') : # q 키 입력 시 녹화 종료
                i = 10 # 루프 종료용 변수 값 설정
                break 

        if 'out' in locals(): # 영상 파일 객체가 생성된 경우
            out.release() # 영상 파일 객체 해제
        if(i == 10):
            break 

    except Exception as e:
        print("Exception occurred:", e)
        break

video.release()
cv2.destroyAllWindows()
