import cv2
import numpy as np
import LaneRecog as LR
filename = './DVR00035.MP4'
video = cv2.VideoCapture(filename)

if not video.isOpened(): raise Exception("error")
frame = 30.0
delay = int(1000/frame)
frame_cnt = 1
width = 640
height = 480
Threahold = 100
#i=1
while True:
    ret, frames = video.read()
    frames = cv2.resize(frames,(width,height))
    if not ret or cv2.waitKey(delay) >= 0: break
    
    InterestArea = LR.InterestRegion(frames,width,height)
    #canny = LR.Canny(InterestArea)
    cv2.imshow('orginal',frames)
    
    canny = LR.Canny(frames)
    cv2.imshow('Mask',InterestArea)
   
    lines = cv2.HoughLinesP(canny, 1.2, np.pi / 180, Threahold, minLineLength=100, maxLineGap=60)
      
       
    #cv2.line(frames, (i[0][0], i[0][1]), (i[0][2], i[0][3]), (255, 0, 255), 1)
            
    # Origin Frame------------------------
    cv2.circle(frames, (int(width * 0.2), int(height * 0.55)), 5, (255, 255, 255), -1)
    cv2.circle(frames, (int(width * 0.8), int(height * 0.55)), 5, (255, 255, 255), -1)
    #cv2.imshow('red_line',frames)
    
    
    blue, green, red = cv2.split(frames)
    
    if(cv2.waitKey(27)>0):
          break

video.release()
cv2.destroyAllWindows()