// #define _DEBUG
#define _RELEASE
#include <Arduino_LSM9DS1.h>
#include <ArduinoBLE.h>

BLEService sensorService("de1b9607-4b2f-4888-848f-003c407a0edd");
BLEStringCharacteristic xSensorLevel("741c12b9-e13c-4992-8a5e-fce46dec0bff", BLERead | BLENotify, 15);
BLEStringCharacteristic ySensorLevel("baad41b2-f12e-4322-9ba6-22cd9ce09832", BLERead | BLENotify, 15);
BLEStringCharacteristic zSensorLevel("5748a25d-1834-4c68-a49b-81bf3aeb2e50", BLERead | BLENotify, 15);

// last sensor data
// float oldXLevel = 0;
// float oldYLevel = 0;
// float oldZLevel = 0;
int16_t oldXLevel = 0;
int16_t oldYLevel = 0;
int16_t oldZLevel = 0;
long previousMillis = 0;

void setup() {
  // put your setup code here, to run once:
#ifdef _DEBUG
  Serial.begin(115200);
  while (!Serial)
    ;
#endif //_DEBUG
  if (!IMU.begin()) {
#ifdef _DEBUG
    Serial.println("Failed to initialize IMU!");
#endif //_DEBUG
    while (1)
      ;
  }

  pinMode(LED_BUILTIN, OUTPUT);
  if (!BLE.begin()) {
#ifdef _DEBUG
    Serial.println("starting BLE failed!");
#endif //_DEBUG
    while (1)
      ;
  }
  BLE.setLocalName("Gyroscope");
  BLE.setAdvertisedService(sensorService);
  sensorService.addCharacteristic(xSensorLevel);
  sensorService.addCharacteristic(ySensorLevel);
  sensorService.addCharacteristic(zSensorLevel);
  BLE.addService(sensorService);
  xSensorLevel.writeValue(String(0));
  ySensorLevel.writeValue(String(0));
  zSensorLevel.writeValue(String(0));
  BLE.advertise();
#ifdef _DEBUG
  Serial.println("Bluetooth device active, waiting for connections...");
#endif //_DEBUG  
}
unsigned long pre_time, cur_time, time_period;
void loop() {
  // put your main code here, to run repeatedly:
  BLEDevice central = BLE.central();
  if (central) {
#ifdef _DEBUG
    Serial.print("Connected to central: ");
    Serial.println(central.address());
#endif //_DEBUG
    digitalWrite(LED_BUILTIN, HIGH);
    cur_time = millis();
    pre_time = cur_time;
    while (central.connected()) {
      //long currentMillis = millis();
      // if(flag)
      // {
      //   
      //   flag = 0;
      // }
      // else
      // {
        
      // }
      updateGyroscopeLevel();
      delay(10);
    }
    cur_time = millis();
    time_period = cur_time - pre_time;
    digitalWrite(LED_BUILTIN, LOW);
#ifdef _DEBUG
    Serial.print("Disconnected from central: ");
    Serial.println(central.address());
    Serial.print("Connected time period : ");
    Serial.println(time_period);
#endif //_DEBUG
  }
}
void updateGyroscopeLevel() {
  int16_t x, y, z;
  // float x, y, z;
  if (IMU.gyroscopeAvailable()) {
    IMU.readGyroscope(x, y, z);
    if (x != oldXLevel) {
      xSensorLevel.writeValue(String(x));
      oldXLevel = x;
    }

    if (y != oldYLevel) {
      ySensorLevel.writeValue(String(y));
      oldYLevel = y;
    }

    if (z != oldZLevel) {
      zSensorLevel.writeValue(String(z));
      oldZLevel = z;
    }
#ifdef _DEBUG
    Serial.print(x);
    Serial.print('\t');
    Serial.print(y);
    Serial.print('\t');
    Serial.println(z);
#endif //_DEBUG    
  }
}
