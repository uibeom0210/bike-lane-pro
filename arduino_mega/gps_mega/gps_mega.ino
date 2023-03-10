#include <SoftwareSerial.h>
#include <TinyGPS.h>
#define GPSBAUD 9600 //gps 통신

TinyGPS gps;
void getgps(TinyGPS &gps);

void setup() {
  Serial.begin(9600);
  Serial1.begin(GPSBAUD);
	gps = TinyGPS();
}

void loop() {
  while(Serial1.available()) 
  {
    int gpsCode = Serial1.read();
    if(gps.encode(gpsCode))
    {
      getgps(gps);
    }
  }
}

void getgps(TinyGPS &gps)
{
 Serial.print("[GPS][DEV0] ");
  int year; 
  byte month, day, hour, minute, second;
  gps.crack_datetime(&year,&month,&day,&hour,&minute,&second);
  Serial.print(year);Serial.print("/");
  Serial.print(month, DEC);Serial.print("/");
  Serial.print(day, DEC);Serial.print("/");
  Serial.print(hour+9, DEC);Serial.print("/");
  Serial.print(minute, DEC);Serial.print("/");Serial.print(second, DEC);
  Serial.print(",");

  gps.f_get_position(&latitude, &longitude);
  Serial.print(latitude,5);
  Serial.print(",");
  Serial.print(longitude,5);
  Serial.print(",");
  Serial.println(gps.f_speed_kmph());
  
  unsigned long chars;
  unsigned short sentences, failed_checksum;
  gps.stats(&chars,&sentences,&failed_checksum);
}