#include <SPI.h>
#include <LoRa.h>
#include <WiFi.h>
#include "time.h"

const char *ssid     = "ZTE_2.4G_K3XPgZ";
const char *password = "5cCTqPbS";

const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 19800;
const int   daylightOffset_sec = 0;

int s;
const int numReadings = 10;
int sstrength[numReadings];
int ind = 0;

#define greenPin 4
#define yellowPin 21
#define redPin 22
int counter = 0;

void setup() {
  pinMode(greenPin, OUTPUT);
  pinMode(yellowPin, OUTPUT);
  pinMode(redPin, OUTPUT);

  Serial.begin(115200);
  while (!Serial);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Initialize NTP
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);

  Serial.println("LoRa Receiver");
  LoRa.setPins(5, 15, 2);

  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  LoRa.setSyncWord(0xA5);
}

void loop() {
  // try to parse packet
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
      Serial.println("Failed to obtain time");
      return;
    }
    
    // Format time
    char timeStringBuff[50];
    strftime(timeStringBuff, sizeof(timeStringBuff), "%Y-%m-%d %H:%M:%S", &timeinfo);
    String receiveTimeString(timeStringBuff);

    // received a packet
    

    

    // read packet
    while (LoRa.available()) {
      Serial.print((char)LoRa.read());
    }

    // print RSSI of packet
    Serial.print("' with RSSI ");
   
    s = LoRa.packetRssi();
    Serial.println(s);
     Serial.print("Received packet '");
    
    Serial.print("' at ");
    Serial.print(receiveTimeString);
    Serial.print(" - ");

    sstrength[ind] = s;
    ind = (ind + 1) % numReadings;

  }
}