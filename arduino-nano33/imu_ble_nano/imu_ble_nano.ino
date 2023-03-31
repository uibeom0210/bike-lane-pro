//#define _DEBUG
#define _RELEASE
//#define _IMU_SENSOR_2D_
#define _IMU_SENSOR_2F_
// #define _IMU_SENSOR_63_
#include <Arduino_LSM9DS1.h>
#include <ArduinoBLE.h>
#include <mbed.h>

//사용 Arduino nano33
#ifdef _IMU_SENSOR_2D_ 
BLEService sensorService("de1b9607-4b2f-4888-848f-003c407a0edd");
// BLEStringCharacteristic accelSensorLevel("741c12b9-e13c-4992-8a5e-fce46dec0bff", BLENotify, 30);
BLEStringCharacteristic accelSensorLevel("741c12b9-e13c-4992-8a5e-fce46dec0bff", BLERead | BLENotify, 30);
BLEStringCharacteristic gyroSensorLevel("baad41b2-f12e-4322-9ba6-22cd9ce09832", BLERead | BLENotify, 30);
BLEStringCharacteristic magnSensorLevel("5748a25d-1834-4c68-a49b-81bf3aeb2e50", BLERead | BLENotify, 30);
#endif
#ifdef _IMU_SENSOR_63_
BLEService sensorService("18e678f5-1be5-46a7-a8f9-56f740244fc1");
// BLEStringCharacteristic accelSensorLevel("9d539e99-115c-485b-951d-cbd263821db7", BLENotify, 30);
BLEStringCharacteristic accelSensorLevel("9d539e99-115c-485b-951d-cbd263821db7", BLERead | BLENotify, 30);
BLEStringCharacteristic gyroSensorLevel("9adda6b7-219a-412c-aeba-976da3e92f10", BLERead | BLENotify, 30);
BLEStringCharacteristic magnSensorLevel("b06d628d-1889-457a-a1a8-5f7adeed4941", BLERead | BLENotify, 30);
#endif

#ifdef _IMU_SENSOR_2F_
BLEService sensorService("20b55a1b-e14a-4f1d-999a-b63ebba09b61");
BLEStringCharacteristic accelSensorLevel("f3f014e9-e1c9-4ab4-9542-44ff558ceb95", BLERead | BLENotify, 30);
BLEStringCharacteristic gyroSensorLevel("3e03fe4b-692f-4f66-8ec2-9efdf7646357", BLERead | BLENotify, 30);
BLEStringCharacteristic magnSensorLevel("e8ea1646-a319-40bb-9872-cf6370174819", BLERead | BLENotify, 30);
#endif

//timer 
using namespace std::chrono;
mbed::Ticker counterTicker;
int connect_flag = 0;
int timer_flag = 0;

// last sensor data
int16_t oldLevelgyro[3] = { 0 };
int16_t oldLevelAccel[3] = { 0 };
int16_t oldLevelMagn[3] = { 0 };
String accelStringData = "";
String gyroStringData = "";
String magnStringData = "";
long previousMillis = 0;

void ISRcounter(void)
{
  timer_flag = 1;
}

void setup() {
  // put your setup code here, to run once:
#ifdef _DEBUG
  Serial.begin(115200);
  while (!Serial)
    ;
#endif  //_DEBUG
  if (!IMU.begin()) {
#ifdef _DEBUG
    Serial.println("Failed to initialize IMU!");
#endif  //_DEBUG
    while (1)
      ;
  }
  pinMode(LED_BUILTIN, OUTPUT);
  if (!BLE.begin()) {
#ifdef _DEBUG
    Serial.println("starting BLE failed!");
#endif  //_DEBUG
    while (1)
      ;
  }
  #ifdef _IMU_SENSOR_2D_
  BLE.setLocalName("IMU_SENSOR_2D");
  #endif
  #ifdef _IMU_SENSOR_63_
  BLE.setLocalName("IMU_SENSOR_63");
  #endif
  #ifdef _IMU_SENSOR_2F_
  BLE.setLocalName("IMU_SENSOR_2F");
  #endif
  BLE.setAdvertisedService(sensorService);
  sensorService.addCharacteristic(accelSensorLevel);
  // sensorService.addCharacteristic(gyroSensorLevel);
  // sensorService.addCharacteristic(magnSensorLevel);
  BLE.addService(sensorService);
  accelSensorLevel.writeValue(String(0));
  // gyroSensorLevel.writeValue(String(0));
  // magnSensorLevel.writeValue(String(0));
  BLE.advertise();
#ifdef _DEBUG
  Serial.println("Bluetooth device active, waiting for connections...");
#endif  //_DEBUG
}

unsigned long pre_time, cur_time, time_period;
void loop() {
  BLEDevice central = BLE.central();
  if (central) {
#ifdef _DEBUG
    Serial.print("Connected to central: ");
    Serial.println(central.address());
    cur_time = millis();
    pre_time = cur_time;
#endif  //_DEBUG
    digitalWrite(LED_BUILTIN, HIGH);

    counterTicker.attach( ISRcounter, 10ms );
    while (central.connected()) {
      if(timer_flag == 1)
      {
        updateAccelscopeLevel();
        // updateGyroscopeLevel();
        // updateMagnscopeLevel();
        timer_flag = 0;
      }
      else
      {
        
      }
    }
    digitalWrite(LED_BUILTIN, LOW);
    counterTicker.detach();
#ifdef _DEBUG
    cur_time = millis();
    time_period = cur_time - pre_time;
    Serial.print("Disconnected from central: ");
    
    Serial.println(central.address());
    Serial.print("Connected time period : ");
    Serial.println(time_period);
#endif  //_DEBUG
  }
}
void updateAccelscopeLevel() {
  int16_t x, y, z;
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);
    accelStringData = String(x) + "," + String(y) + "," + String(z) + "," ;
    accelSensorLevel.writeValue(accelStringData);
  }
#ifdef _DEBUG
  Serial.println(accelStringData);
#endif  //_DEBUG
}

void updateGyroscopeLevel() {
  int16_t x, y, z;
  if (IMU.gyroscopeAvailable()) {
    IMU.readGyroscope(x, y, z);
    gyroStringData = String(x) + "," + String(y) + "," + String(z) + "," ;
    gyroSensorLevel.writeValue(gyroStringData);
  }
#ifdef _DEBUG
  Serial.println(gyroStringData);
#endif  //_DEBUG
}
void updateMagnscopeLevel() {
  int16_t x, y, z;
  if (IMU.magneticFieldAvailable()) {
    IMU.readMagneticField(x, y, z);
    magnStringData = String(x) + "," + String(y) + "," + String(z);
    magnSensorLevel.writeValue(magnStringData);
  }
#ifdef _DEBUG
  Serial.println(magnStringData);
#endif  //_DEBUG
}
