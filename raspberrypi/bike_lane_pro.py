import pandas as pd
import numpy as np
import os.path
import os
import matplotlib.pyplot as plt
import natsort
import folium
from folium.plugins import MarkerCluster
from datetime import datetime, timedelta
from haversine import haversine # distance measurement
from PIL import Image
import io
import base64

class FileSystem:
    """
    ### Label SWS, video data.

        1. label SWS data and video data by the time.
        2. get the pothole zone data.
        3. get the GPS coordinates at the pothole zone.
        4. get the roughness data
        5. upload data
    """
    def __init__(self, parent=None):
        super().__init__()
        self.GPS_folder_path = './GPS_copy/'
        self.IMU_folder_path = './IMU_copy/'

    def findRecentFile(self, folder_path, dtype):
        # Sort files up to date
        create_time_list = []
        file_list = os.listdir(f"{folder_path}")

        if dtype == 'video':
            for file in file_list:
                if file.endswith((".csv")):
                    create_time = os.path.getctime(f"{folder_path}{file}")
                    create_time_list.append((file, create_time))
        else:
            for file in file_list:
                if file.endswith(".csv"):
                    create_time = os.path.getctime(f"{folder_path}{file}")
                    create_time_list.append((file, create_time))

        sorted_file_list = sorted(create_time_list, key=lambda x: x[1], reverse=True)
        # print(sorted_file_lst)
        recent_file = (sorted_file_list[0])[0]
        # print(recent_file_name)
        return recent_file

    # def readCsvFile(self, dtype) :
    #     '''
    #     Read csv file
        
    #         1. find recent csv file in the ec2.
    #         2. read csv file.
    #     '''
    #     if dtype == 'IMU':
    #         IMU_file = self.findRecentFile(self.IMU_folder_path,'csv')
    #         imu_file = pd.read_csv(self.IMU_folder_path + IMU_file)
    #         print(IMU_file)
    #         return imu_file
    #     elif dtype == 'GPS':
    #         GPS_file = self.findRecentFile(self.GPS_folder_path,'csv')
    #         gps_file = pd.read_csv(self.GPS_folder_path + GPS_file)
    #         return gps_file

class ReceiveDataLabeling: 
    """
    ### Label SWS, video data.

        1. label SWS data and video data by the time.
        2. get the pothole zone data.
        3. get the GPS coordinates at the pothole zone.
        4. get the roughness data
        5. upload data
    """
    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.fileSystem= FileSystem()
        self.myGPS = GPS()
        self.visualization = Visualization()
        self.IMU_file = self.fileSystem.findRecentFile(self.fileSystem.IMU_folder_path,'csv')
        self.IMU_data = pd.read_csv(self.fileSystem.IMU_folder_path + self.IMU_file)
        self.GPS_file = self.fileSystem.findRecentFile(self.fileSystem.GPS_folder_path,'csv')
        self.myGPS.get_gpsdata(self.fileSystem.GPS_folder_path + self.GPS_file)
        self.data_length = len(self.IMU_data)

        # sws labeling
        self.labeling_list = []
        self.front_index = 0
        self.back_index = 0
        self.last_index = 0
        self.valuelist = [] # pothole severity -> list
        self.value = 0  # pothole severity
        self.ph_location = []
        self.addlistcnt = 0

        # video labeling
        self.out = []
        self.max_frame = 0
        self.cap = 0
        self.vfilename = []

        # algorithm
        self.gm2ws = Accel2Wheelspeed()
        self.previous_whspeed = 0
        self.potholeLevel = PotholeLevel()
        self.rnIdxlist = []
        self.rnIdxlist_raw = []

    def run(self):
        sws_data = self.IMU_data
        errorcnt = 0
        location = self.ph_location
        lasttime = self.myGPS.get_lasttime()
        print("last time :",lasttime)

        print("labeling...")
        for index, row in sws_data.iterrows():
            try:
                if row['time'] > lasttime:
                    break
                accel_x = row.AccelX
                accel_y = row.AccelY      

                wheelSpeed, r = self.gm2ws.runRT_singleChannel(accel_x) # gyro, magnetic to wheelspeed
                self.potholeLevel.getData(accel_x, accel_y)

                if wheelSpeed != "noUpdate":
                    gps_Speed = self.myGPS.get_speed(row) # gps speed
                    # if gps_Speed == 0:
                    #     gps_Speed = wheelSpeed#self.previous_whspeed
                    # self.previous_whspeed = gps_Speed
                    self.potholeLevel.getSpeed(wheelSpeed)
                    print('wheelspeed:', wheelSpeed, gps_Speed)
                else:
                    pass

                value, maxMagspot = self.potholeLevel.detectImpact(index)
                # print(value)

                if value > 0:
                    print('impact POP, pothole level:',str(value), str(index))
                    # self.pothole_label(maxMagspot, value) # labeling around the pothole
                    ph_coordinates = self.myGPS.get_coord(sws_data, maxMagspot) # impact coordinates
                    moment = sws_data.iloc[maxMagspot]['time'] # impact moment
                    ph_datetime = str(self.addlistcnt-1)
                    location.append([round(moment), ph_coordinates[0], ph_coordinates[1], value])
                    print(location[-1])
                    # print('MM:',maxMagspot)
                else:
                    pass

            except Exception as e:
                errorcnt += 1
                print('error run:',e)
                print('index:',index)
                if errorcnt > 10:
                    break
                else:
                    pass

        print('errorcnt: ', errorcnt)
        self.ph_location = location

    def pothole_label(self, index, value):
        '''
        Label around the pothole zone

            1. if the impact happens again soon, just tie it up and label it. criterion : index lenth 300
            2. add pothole severity together
        '''
        addcnt = 0
        try:
            if index < self.last_index + 300:
                if not self.labeling_list:
                    self.value = value
                    self.valuelist.append(self.value)
                    self.labeling_list.append([self.front_index, self.back_index])
                    print('add list1')
                    addcnt += 1

                if (index + 300) > (self.data_length-1):
                    self.back_index = (self.data_length-1)
                else:
                    self.back_index = index + 300

                self.front_index = self.front_index
                self.last_index = self.back_index
                self.labeling_list.pop()
                if self.value > value:
                    pass
                else:
                    self.value = value
                self.valuelist.append(self.value)
                self.labeling_list.append([self.front_index, self.back_index])
            else:
                if (index + 300) > (self.data_length-1):
                    self.back_index = (self.data_length-1)
                else :
                    self.back_index = index + 300

                self.front_index = index - 300
                self.last_index = self.back_index
                self.value = value
                self.valuelist.append(self.value)
                self.labeling_list.append([self.front_index, self.back_index])
                print('add list2')
                addcnt += 1

            self.addlistcnt += addcnt
            # print('new label:', self.front_index, self.back_index)
        except Exception as e:
            print('error', e)
            # print('last label:', self.labeling_list[-1], self.front_index, self.back_index)

    def data_processing(self):
        '''
        Process the data. Get four kinds of data.

            1. pothole labeling sws data
            2. pothole labeling video data
            3. roughness/roughness raw data
            4. location {time - pothole gps(latitude, longitude) - pothole severity} data
        '''
        self.run()
        sws_data = self.IMU_data
        sws_indexlist = self.labeling_list
        sws_valuelist = self.valuelist
        sws_timelist = self.myGPS.index2time(sws_data, sws_indexlist)
        sws_indexlist = self.myGPS.time2index(sws_data, sws_timelist)

        # pothole labeling sws data
        ph_swslist = []
        datalist = []
        valuelist = []
        cnt = 0
        for index, row in enumerate(sws_indexlist):
            datalist.append(sws_data.iloc[row[0]:row[1]])
            valuelist.append(sws_valuelist[index])
            cnt += 1
        ph_swslist = [datalist, valuelist]
        print("made datalist : ", cnt)

        # create/remove folder
        now = datetime.now()
        nowdate = now.strftime('%Y-%m-%d')
        directory = '/home/pi/Desktop/'+ nowdate +'/'
        self.createFolder(directory)

        name = (self.IMU_file.split('_')[1]).split('.')[0]

        # self.ph_location data = [time - pothole_gps - pothole severity]
        df = pd.DataFrame(self.ph_location, index = None, columns = ['time', 'latitude', 'longitude', 'severity'])
        df.astype({ 'time' : 'int' })
        self.visualization.get_phdata(df)

    def uploaddata(self):
        '''Upload all data and print out file for visualization'''
        ph_df = self.data_processing()
        print('data uploading...')
        print('data accumulating...')
        self.visualization.accumulate()
        self.visualization.visualize()

    def createFolder(self, directory):
        '''
        Create folder

            create a folder if it does not exist
        '''
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print ('Error: Creating directory. ' +  directory)
    

class GPS:
    """
    ### Obtain GPS time, coordinates, speed
    
        1. getXXX: get value from somewhere else
        2. load subtitle data
        3. convert time to index, index to time
    """
    def __init__(self, parent=None):
        super().__init__()
        self.gps_data = ""
        self.datalength = len(self.gps_data)
    # get
    def get_gpsdata(self, path):
        self.gps_data = pd.read_csv(path)
        return self.gps_data

    def get_lasttime(self):
        gpsdata = self.gps_data
        lasttime = gpsdata.iloc[-1]['datetime']
        return lasttime

    def get_time(self, datalist):
        '''Match the gps time and whatever time'''
        tmlblist = []
        gpsdata = self.gps_data
        for label in datalist:
            # print(label['datetime'].iloc[0], label['datetime'].iloc[-1])
            fronttime = gpsdata.index[gpsdata['datetime'] >= label[0]].tolist()[0]
            backtime = gpsdata.index[gpsdata['datetime'] <= label[1]].tolist()[-1]
            tmlblist.append([fronttime,backtime])
        return tmlblist

    def get_speed(self, row_data):
        '''Get gps speed'''
        gps_data = self.gps_data        
        gps_index = gps_data.index[gps_data['datetime'] >= row_data['time']].tolist()[0]
        speed = gps_data.iloc[gps_index]['speed']
        return speed

    def get_coord(self, data, index):
        '''Get latitude and longitude of the index'''
        gps_data = self.gps_data
        # print('got gps, index:',index)
        gps_index = gps_data.index[gps_data['datetime'] >= data.iloc[index]['time']].tolist()[0]
        # print('got gps index')
        latitude = gps_data.iloc[gps_index]['latitude']
        longitude = gps_data.iloc[gps_index]['longitude']
        ans = [latitude, longitude]
        return ans

    # convert
    def index2time(self, data, idxlblist):
        '''Index to time value'''
        tmlblist = []
        for label in idxlblist:
            fronttime = int(data.iloc[label[0]]['time'])
            backtime = int(data.iloc[label[1]]['time'])
            tmlblist.append([fronttime,backtime])
        return tmlblist
    
    def time2index(self, data, tmlblist):
        '''Time to index value'''
        idxlblist = []
        for label in tmlblist:
            frontidx = data.index[data['time'] >= label[0]].tolist()[0]
            backtidx = data.index[data['time'] <= label[1]].tolist()[-1]
            idxlblist.append([frontidx, backtidx])
        return idxlblist

#####################################################################################
# Algorithm for development, add fuction
#####################################################################################

"""
for development, add fuction
"""
def mean(a):
    return sum(a)/len(a)

def p2p(data):
    p2p = data.max() - data.min()
    return p2p

class Accel2Wheelspeed(object):
    def __init__(self, axis = ["AccelX",], segmentSize = 100, segmentDelta = 50, MAsize = 2, MAdelta = 1): 
        # self.targetData = inputData[axis]
        self.axis = axis
        self.samplingRate = 59.5
        
        self.realtimeDetection = False
        
        self.segmentSize =   segmentSize  # 100
        self.segmentDelta =  segmentDelta  # 50
        
        self.MAsize =   MAsize
        self.MAdelta =  MAdelta
        
        # self.threshold = 0.4 # noise is 0.05~0.11, signal is 0.8~1.05 in first test
        self.threshold = 500 # for rawData

        
        self.segSize_afterMA = round((self.segmentSize-self.MAsize) / self.MAdelta +1)
        self.segDelta_afterMA = round((self.segmentDelta) / self.MAdelta)

        self.R = 0.6096  # Diameter of bicycle tire
        self.zcrResolution = self.R * 3.141592653589793 *self.samplingRate / self.segmentSize *3.6 # *3.6 is for m/s->km/h
       # self.howManyPass = round(39 / self.MAdelta * 0.73) # 39 need to be changed with calculation from tire size and max speed
        self.speedPerOneturntime = self.R * 3.141592653589793 * self.samplingRate * 3.6 / self.MAdelta

        self.rtData = []
        
    def MA(self, data): #for all axis
        afterMA = []
        for i in range(self.MAsize, len(data), self.MAdelta):
            afterMA.append(mean(data[i-self.MAsize:i]))
        afterMA = pd.DataFrame(afterMA)
        return afterMA[0]
    
    # Magnetostriction Coupling Ratio    
    # 부호 변동이 얼마나 이뤄지는지에 대한 보정값과 평균값.
    def MCRcount(self, data, plus2minus = True):
        mcrCount = 0
        if plus2minus == False:
            data = data * -1
        ####################################################
        mean_data = mean(data)
        # print(type(data))
        pre_data = data[data.index[0]]
        #doPass = 0

        #현재 데이터 값이 평균값보다 작을 때
        #이전 데이터 값이 평균값보다 큰 값이었을 때 mcrcount를 1씩 증가시킨다.
        if p2p(data) < self.threshold: # 데이터의 peek to peek 값이 threshold보다 작다면 MCR은 0이므로 0을 바환한다
            return 0
        for over_th_data in data[1:]: # 데이터 한바퀴
            if over_th_data < mean_data: #데이터 값이 평균보다 작다면
                if pre_data > mean_data: #초기 데이터가 평균 데이터보다 크다면
                    mcrCount += 1 #count 1 증가
                    # doPass = self.howManyPass 
                    pre_data = over_th_data #초기 데이터를 다음 데이터로 갱신
                else:
                    pass
            elif pre_data < mean_data:  #초기 데이터가 평균 데이터보다 작다면
                pre_data = over_th_data #갱신
            else:
                pass
        return mcrCount

    def MCRcount_singleChannel_RT(self, data, plus2minus = True):
        MCR = self.MCRcount(data[0:self.segSize_afterMA], plus2minus = plus2minus)

        # MCR = pd.Series(MCR)
        MCRspeed = MCR*self.zcrResolution
        return MCRspeed, MCR
    
    def runRT_singleChannel(self, data):
        # data: 4k len
        afterMAs = []
        if len(self.rtData) < self.segmentSize:
            self.rtData.append(data)
            return 'noUpdate', 'noUpdate'
        else:
            afterMAs.append(self.MA(self.rtData))
            self.rtData = []
            speed_p, mcr_p = self.MCRcount_singleChannel_RT(afterMAs[0])
            speed_m, mcr_m = self.MCRcount_singleChannel_RT(afterMAs[0], plus2minus = False)
            # print((speed_p + speed_m) /2)
            return (speed_p + speed_m) /2 , (mcr_p + mcr_m) /2

class PotholeLevel(object):
    """
    calculate and return
        pothole len, depth, severity
    
    setXXX: calculate something i.n this class for internal use
    calXXX: calculate something in this class
    getXXX: get value from somewhere else
    """
    def __init__(self):
        super(PotholeLevel, self).__init__()
        self.sensorPosition = None
        self.frontRearLen = 1.60 # [m]
        self.freq = 1600
        
        self.carSpeed = 0 # [km/h]
        # self.frontRearTime = self.frontRearLen /(self.carSpeed/3.6) *self.freq # [sample]
        
        self.threshold = 5000 # 2500
        self.threshold_lvl1 = 0
        self.threshold_lvl2 = 0
        self.windowSize = 0
        self.phase = 0
        self.aXdata = []
        self.aYdata = []
        self.aMagdata = []

        self.impactTimeCount = 0
        
    def calMag(self):
        value = (self.aXdata[-1]**2 +  self.aYdata[-1] **2) **0.5
        self.aMagdata.append(int(value))
        
    def MA(self, data, window, delta):
        pass
    
    def getData(self, aX, aY):
        self.aXdata.append(aX)
        self.aYdata.append(aY)
        self.calMag()
        
    def detectImpact(self, index):
        """
        level -1: no result
        level  0: no pot hold
        level  1: mild pot hold
        level  2: severe pot hold
        """
        if self.impactTimeCount > 0:
            try:
                self.impactTimeCount -= 1
                if self.impactTimeCount == 0:
                    maxMag = max(self.aMagdata[-self.windowSize:])
                    # print('maxmag:',maxMag,'index:',index,'threshold_lvl1:',self.threshold_lvl1,'threshold_lvl2:',self.threshold_lvl2)
                    if maxMag > self.threshold_lvl2:
                        maxidx = self.aMagdata[-self.windowSize:].index(maxMag)
                        level = 2
                    elif maxMag > self.threshold_lvl1:
                        maxidx = self.aMagdata[-self.windowSize:].index(maxMag)
                        level = 1
                    else:
                        maxidx = 0
                        level = 0
                    return level, index - self.windowSize + maxidx
            except Exception as e:
                print('exception.', e)
                pass

        elif self.detectOverThreshold() == True:
            self.impactTimeCount = self.setWindow()
            self.setThreshold()
            # self.deltaAccum = 0
        return -1, 0
    
    def setWindow(self):
        answer = (self.carSpeed *(-5) + 700)
        if answer < 500:
            answer
        elif answer > 600:
            answer = 600
        self.windowSize = int(answer)
        return self.windowSize

    def setThreshold(self):
        answer = 1000 * self.carSpeed
        if answer < 15000:
            answer = 15000
        elif answer > 40000:
            answer = 40000
        self.threshold_lvl2 = answer
        self.threshold_lvl1 = self.threshold_lvl2 * 0.45
        
    def eraseOldData(self):
        if len(self.aXdata) > 1000:
            self.aXdata = self.aXdata[200:]
            self.aYdata = self.aYdata[200:]
            self.aMagdata = self.aMagdata[200:]

    def detectOverThreshold(self):
        if self.aMagdata[-1] > self.threshold:
            return True
        else:
            return False

    def getSpeed(self, speed_km_h):
        self.carSpeed = speed_km_h

class Visualization: 
    """

    """
    def __init__(self, parent=None):
        super().__init__()
        self.ph_remain = pd.read_csv('/home/pi/Desktop/GRID/pothole_gps.csv')
        self.ph_newdata = []
        self.image_list = []

    def accumulate(self):
        '''Accumulate data for visualization'''
        self.ph_remain = self.concat_ph(self.ph_remain, self.ph_newdata)
        self.gpsprint()


    def concat_ph(self, remain, new):
        '''Append new pothole location'''
        # print(remain)
        if new.empty:
            return remain
        else:
            new = self.remove_overlap(remain, new)
            # print(new)
            # result = remain.append(new)
            return new
        
    def gpsprint(self):
        '''Print out the file for visualization'''
        ph = self.ph_remain
        ph.to_csv("/home/pi/Desktop/GRID/pothole_gps.csv", index=None)
    
    def getImagePothole(self):
        image_path = "./CAM/"
        image_file_list = []
        image_tag_list = []
        file_list = os.listdir(f"{image_path}")

        for file in file_list:
            if file.endswith((".jpg")):
                image_file_list.append(file)
                print((file.split('_')[1]).split('.')[0])
                self.image_list.append((file.split('_')[1]).split('.')[0])
        for file in image_file_list:
            # 이미지 파일 열기
            image = Image.open(f"./CAM/{file}")
            # 이미지 데이터 가져오기
            img_data = io.BytesIO()
            image.save(img_data, format='JPEG')
            img_data.seek(0)
            img_bytes = img_data.read()
            # HTML 이미지 태그 생성
            image_tag = '<img src="data:image/jpeg;base64,{}">'.format(base64.b64encode(img_bytes).decode())
            image_tag_list.append(image_tag)
            
        return image_tag_list
        
    def remove_overlap(self, exist, new):
        '''Remove overlap data'''
        columns = ['time', 'latitude', 'longitude', 'severity']
        new_df = pd.DataFrame(index = None, columns = columns)
        if exist.empty:
            exist = exist.append(pd.DataFrame([new.iloc[0]], columns = columns), ignore_index = True)

        for new_index, new_row in new.iterrows():
            same_cnt = 0
            for ex_idx, ex_row in exist.iterrows():
                # print(ex_idx)
                distance = haversine((ex_row['latitude'], ex_row['longitude']), (new_row['latitude'], new_row['longitude']), unit = 'm')
                if distance < 3:
                    # print('same')
                    # print(distance)
                    same_cnt += 1
                else:
                    # print(distance)
                    pass
            if same_cnt == 0:
                # print('newpush')
                exist = exist.append(pd.DataFrame([new_row.tolist()], columns = columns), ignore_index = True)
            else:
                pass
        return exist
    
    def get_phdata(self, df):
        self.ph_newdata = df

    def visualize(self):
        image_tag_list = self.getImagePothole()
        tiles = ["OpenStreetMap", 'Stamen Toner', 'cartodbpositron']
        print(self.ph_remain)
        m = folium.Map(location = [self.ph_remain["latitude"][0], self.ph_remain["longitude"][0]],tiles=tiles[0],zoom_start=12, max_zoom=19)
        marker_cluster = MarkerCluster().add_to(m)
        for index, row in self.ph_remain.iterrows():
            if row.severity == 2:
                color = 'red'
            elif row.severity == 1:
                color = 'orange'
            lat = row['latitude']
            lon = row['longitude']
            time = str(int(row['time']))
            severity = row['severity']
            print(time)
            # folium 팝업 생성
            print(self.image_list)
            if time in self.image_list:
                print("image link!")
                image_tag = image_tag_list[self.image_list.index(time)]
                print(self.image_list.index(time))
                new_popup = folium.Popup(image_tag, max_width=640)
            else :
                new_popup = severity
            folium.Marker(location = [lat, lon],
                            icon=folium.Icon(color = color),
                            popup=new_popup).add_to(marker_cluster)
        m.save('/home/pi/Desktop/m_visualization.html')
        os.system("sudo mv /home/pi/Desktop/m_visualization.html /var/www/html/m_visualization.html")
labeling = ReceiveDataLabeling()
labeling.uploaddata()