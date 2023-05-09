# BikeLanePro
"BikeLanePro" is a comprehensive system designed to efficiently manage and maintain bicycle lanes throughout the city, ensuring safe and convenient cycling for all.

## Concept and Flow


<p align="center">
  <img src=https://drive.google.com/uc?export=download&id=1Ko4wG_dqFkLE8rinuPx64A2UAnMDRWQ3>
  <img src=https://drive.google.com/uc?export=download&id=1Jh3LkXimsisHMwxDLFG5dwWorD1DEDpf>
</p>

**This project was developed using a variety of boards. Arduino Mega, Arduino nano 33 BLE, Jetson Nano Board, and Raspberry Pi were mainly used, and C was used to develop the Arduino boards. The Raspbian environment was used to communicate with the Pi.** <br>

**The difference between Jetson and Pi is that Jetson uses Pytorch and Open CV for image processing and object recognition, while Pi acts as a server and is mainly responsible for communication, data reception, and storage. Jetson was able to train data through the co-lab and check the accuracy of the trained data using Tensor Board. Jetson mainly used "VScode" to configure the development environment.** <br>

### Aggregating data
---
<p align="center">
  <img src=https://drive.google.com/uc?export=download&id=1o8qNduVzn4C3Gpy6f0oIF1yhGfBiM609>
</p>

**Unlike video data, the acceleration and GPS sensor data needed to be transmitted directly from the sensors and converted in a way that was efficient and easy to use within the project. Therefore, the team pre-defined a certain protocol format for transmitting and receiving sensor data and proceeded accordingly. The basic format of the protocol is as follows: 'DEVICE' contains 'IMU', 'GPS', and 'SEQUENCE' contains the order in which the sensor received the data. 'DATA' contains the actual data received by the sensor, which is organized into delimiters for easy extraction.**

### Communication with Raspberry Pi
<p align="center">
  <img src=https://drive.google.com/uc?export=download&id=1f54PeUNQJo7_Sso-cpwGMVPlKx2L5m18 align="center" width="49%">
  <img src=https://drive.google.com/uc?export=download&id=1LZ3s-6fBheYyuijX0T2PG-7ZlusRhtRf align="center" width="49%">
  <figcaption align="center"></figcaption>
</p>
<p align="center">
    <img src=https://drive.google.com/uc?export=download&id=1jporZLQMbmKo9lqd8xCyz_okGFifH8LT align="center">
</p>

## The speed of a bicycle
<br>
<img src=https://drive.google.com/uc?export=download&id=1eCub96Qh37wQe51D_orR129Kb8iQu3tP align="center">
</br>

 **After analyzing the acceleration sensor, we found that the higher the speed of the bike, the greater the value of the acceleration sensor in the "potholes" on the road. Therefore, it was essential to calculate the speed of the bike.** <br>
 **The measurement period is one minute, and about 50-60 data points are stored every second. Taking losses into account, a single file contains more than 3,000 pieces of data. The data is segmented into small units at regular intervals, and the average value of each unit is averaged to perform noise smoothing.**<br>
 **First, we need to calculate the unit velocity of a waveform using the wheel circumference and sampling frequency, and then calculate how many waves occur in each segment. To do this, we count how many times the sensor value crosses the bin, relative to the bin-wide average. Finally, multiply the number of counts by the unit velocity to derive the speed of the bike.**<br>
 ## Implementing the Pothole Impact algorithm
 <p align="center">
    <img src=https://drive.google.com/uc?export=download&id=1qUxWdTUSzsqaf3MSzTgKJWnAzOWelwf_ align="center">
</p>

**Based on the results from the accelerometer analysis tool, set the threshold value for Pothole to 15000 or higher. Create a baseline value to compare this threshold value to, and adjust it so that the faster the bike is going, the harder it is to cross the threshold.
 If an impact value is detected, we extract the time information at that point in time and match it to the time information in the GPS data. This extracts the coordinates and creates a CSV file containing the time, coordinates, and information about the severity of the 'Pothole'.
 This requires that the bike's accelerometer data and GPS data are accurately synchronized based on time information. This CSV file is then used for subsequent analysis and visualization.**
 </br>
 ## Creating and training datasets
![](https://drive.google.com/uc?export=download&id=12jVzENYQ14KtviL6QQ0fnQDJQyrIcdVH)
**The three types of objects we wanted to recognize were potholes, manholes, and bike markings. Most of the database construction was done through Roboflow. In Robofow, pothole and manhole datasets were already configured, so we mainly downloaded them, and since we couldn't find 'bike marking' data, we took pictures and collected datasets for training.**<br>
![](https://drive.google.com/uc?export=download&id=1-Xv10DqH79Wq1lHEkvru2rluBXjWKKjg) |![](https://drive.google.com/uc?export=download&id=11dXrT1I_nhj6OMexpp8UwD7pKpFiR_dH)
--- | --- | 

**A graph is also presented to check the final dataset, which shows that the lines for each class overlap closely as they are trained and at the right ratio. From this, we can see that we have created a good final dataset by setting the appropriate data group ratio, marking the objects clearly when selecting data, and uploading the missing data by taking pictures by hand. In particular, it is important to note that after validating the final dataset, you can check how well the test group photos recognize the objects. This allows us to evaluate the accuracy of our weighting model and look for ways to improve it. This article highlights the use of various techniques for object detection and the resulting weighting model with high accuracy. It is also mentioned that efforts were made to set the data group ratio and select the data, which shows that proper data preprocessing and training can lead to high accuracy object detection.**

## Apply model learning

![](https://drive.google.com/uc?export=download&id=1kcaYCdDNg-t_0fWBqCERtWLvA0OTcFnD) |![](https://drive.google.com/uc?export=download&id=1JFlTobJZsiH0Au-Tu6TIEL7oVy6f9dpJ)
--- | --- | 
![](https://drive.google.com/uc?export=download&id=1hxkCE5Md3Uaqo4jf6gaHEJmkfMW6vwAE) |![](https://drive.google.com/uc?export=download&id=1iGxM23m0WZXyaILM5UYQCkNWC6KlGd5o)


## Reflections and future directions

- **I was disappointed that we didn't get enough quality data during the model training process, and as a result, there were some manholes and potholes that we didn't recognize. I think the synergy of the devices would have been better if we had accumulated more image data and trained them.**
- **During the demonstration process, it was difficult to find a camera that could be fixed properly because we were using public property. With a more stable camera, it would be possible to get more accurate object recognition through more sophisticated images.**
- **The performance of the GPS model was not very good, so the values were not accurate, and there was an error of around 5-10 meters at a time. It was disappointing that the visualization on the map did not show the exact location, but since it was a cheap model, I think it can be fixed by using an advanced model.**
- **I thought about using the camera in a variety of ways. Currently, we are only checking for damage to bicycle paths, but if the number of recognized objects increases through further training, I think it will be useful for various road environments such as cleanliness based on the amount of trash, walking and driving conditions, and urban policing.
**

# <div align="center"> Thank you </div>
<div align="right"> by Jimyoung98</div>
