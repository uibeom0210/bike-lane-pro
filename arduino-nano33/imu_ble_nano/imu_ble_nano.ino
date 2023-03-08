// #define _DEBUG
#define _RELEASE
#include <Arduino_LSM9DS1.h>
#include <ArduinoBLE.h>

BLEService sensorService("de1b9607-4b2f-4888-848f-003c407a0edd");
BLEStringCharacteristic accelSensorLevel("741c12b9-e13c-4992-8a5e-fce46dec0bff", BLERead | BLENotify, 30);
BLEStringCharacteristic gyroSensorLevel("baad41b2-f12e-4322-9ba6-22cd9ce09832", BLERead | BLENotify, 30);
BLEStringCharacteristic magnSensorLevel("5748a25d-1834-4c68-a49b-81bf3aeb2e50", BLERead | BLENotify, 30);

// last sensor data
int16_t oldLevelgyro[3] = { 0 };
int16_t oldLevelAccel[3] = { 0 };
int16_t oldLevelMagn[3] = { 0 };
String accelStringData = "";
String gyroStringData = "";
String magnStringData = "";
long previousMillis = 0;

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
  BLE.setLocalName("IMU_Sensor");
  BLE.setAdvertisedService(sensorService);
  sensorService.addCharacteristic(accelSensorLevel);
  sensorService.addCharacteristic(gyroSensorLevel);
  sensorService.addCharacteristic(magnSensorLevel);
  BLE.addService(sensorService);
  accelSensorLevel.writeValue(String(0));
  gyroSensorLevel.writeValue(String(0));
  magnSensorLevel.writeValue(String(0));
  BLE.advertise();
#ifdef _DEBUG
  Serial.println("Bluetooth device active, waiting for connections...");
#endif  //_DEBUG
}
// unsigned long pre_time, cur_time, time_period;
void loop() {
  // put your main code here, to run repeatedly:
  BLEDevice central = BLE.central();
  if (central) {
#ifdef _DEBUG
    Serial.print("Connected to central: ");
    Serial.println(central.address());
#endif  //_DEBUG
    digitalWrite(LED_BUILTIN, HIGH);
    // cur_time = millis();
    // pre_time = cur_time;
    while (central.connected()) {
      updateAccelscopeLevel();
      updateGyroscopeLevel();
      updateMagnscopeLevel();
      delay(10);
    }
    // cur_time = millis();
    // time_period = cur_time - pre_time;
    //digitalWrite(LED_BUILTIN, LOW);
#ifdef _DEBUG
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

    accelStringData = "[IMU][Accel]" + String(x) + "," + String(y) + "," + String(z);
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

    gyroStringData = "[IMU][Gyro]" + String(x) + "," + String(y) + "," + String(z) + '\n';
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

    magnStringData = "[IMU][Magn]" + String(x) + "," + String(y) + "," + String(z);
    magnSensorLevel.writeValue(magnStringData);
  }
#ifdef _DEBUG
  Serial.println(magnStringData);
#endif  //_DEBUG
}
