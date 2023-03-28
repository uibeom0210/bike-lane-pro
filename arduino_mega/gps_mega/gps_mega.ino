#include <SoftwareSerial.h>
#include <TinyGPS.h>
#define GPSBAUD 9600  //gps 통신

TinyGPS gps;
void getgps(TinyGPS &gps); //gps 함수 선언

void setup() 
{
  Serial.begin(9600); //시리얼 통신 사용(라즈베리)
  Serial1.begin(GPSBAUD); //시리얼 통신 사용(GPS)
  gps = TinyGPS(); 
}

void loop() 
{
  while (Serial1.available()) //GPS 통신
  {
    int gpsCode = Serial1.read(); 
    if (gps.encode(gpsCode)) 
    {
      getgps(gps); //함수 실행
    }
  }
}

void getgps(TinyGPS &gps) 
{
  char buf[11]; //GPS 값을 저장할 변수
  Serial.print("[GPS][DEV0]"); //팀 프로토콜에 맞춰 GPS데이터 임을 알린다
  int year;
  byte month, day, hour, minute, second; //날짜와 시간 데이터 변수 선언
  gps.crack_datetime(&year, &month, &day, &hour, &minute, &second); 
  sprintf(buf, "%02d", hour+9); Serial.print(buf); //시간 출력
  sprintf(buf, "%02d", minute); Serial.print(buf); //분 출력
  sprintf(buf, "%02d", second); Serial.print(buf); // 초 출력
  // Serial.print(hour + 9, DEC); 
  // Serial.print(minute, DEC);
  // Serial.print(second, DEC);
  Serial.print(",");

  float latitude, longitude; //위도 경도 변수 선언
  gps.f_get_position(&latitude, &longitude); //위도 경도 값 확인
  Serial.print(latitude,8); //소수점 아래 8자리까지 출력
  Serial.print(",");
  Serial.print(longitude,8);
  Serial.print(",");
  Serial.println(gps.f_speed_kmph()); //속도 출력

  unsigned long chars;
  unsigned short sentences, failed_checksum;
  gps.stats(&chars, &sentences, &failed_checksum); //데이터 통계 및 각 변수에 저장합니다.
}