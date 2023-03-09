import cv2
import numpy as np
import LaneRecog as lr
video = cv2.VideoCapture(0)
if not video.isOpened(): raise Exception("error")

frame = 30.0
delay = int(1000/frame)
frame_cnt = 1
width = 640
height = 480
fourcc = cv2.VideoWriter_fourcc(*'XVID')
i=1
cnt=0
while True:
    out = cv2.VideoWriter('/home/jetson/Desktop/project/bike-lane-pro/jetson/opencv_lane_detect/output'+'{}'.format(i)+'.avi',fourcc,frame,(int(width),int(height)))
    cnt = 0
    while(video.isOpened()):
        
        ret, frames = video.read()
        if not ret: break
        cv2.imshow('original',frames)
        out.write(frames)

        cnt = cnt+1
        print(cnt)
        if(cnt == 1000&cv2.waitKey(1)):
            
            i = i +1
            break
    
    if(i==5): break

video.release()
out.release()
cv2.destroyAllWindows()