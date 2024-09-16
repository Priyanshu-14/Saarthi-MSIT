#include <SPI.h>
#include <LoRa.h>
#include <WiFi.h>
#include "time.h"

// WiFi credentials
const char *ssid = "aman";
const char *password = "14189006";

// NTP server details
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 19800;
const int daylightOffset_sec = 0;

// RSSI values
const int numReadings = 10;
int sstrength[numReadings];
int ind = 0;

// LED pins
#define greenPin 4
#define yellowPin 21
#define redPin 22

void setup() {
  // Initialize LED pins
  pinMode(greenPin, OUTPUT);
  pinMode(yellowPin, OUTPUT);
  pinMode(redPin, OUTPUT);

  // Initialize Serial
  Serial.begin(115200);
  while (!Serial);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Initialize NTP
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);

  // Initialize LoRa
  Serial.println("LoRa Receiver");
  LoRa.setPins(5, 15, 2);
  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  LoRa.setSyncWord(0xA5);
}

void loop() {
  // Try to parse packet
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // Get the current time with milliseconds precision
    struct timeval tv;
    gettimeofday(&tv, NULL);
    struct tm* timeinfo = localtime(&tv.tv_sec);

    // Format time with milliseconds (excluding day)
    char timeStringBuff[50];
    snprintf(timeStringBuff, sizeof(timeStringBuff), "%02d:%02d:%02d.%03d",
             timeinfo->tm_hour,
             timeinfo->tm_min,
             timeinfo->tm_sec,
             (int)(tv.tv_usec / 1000));
    String receiveTimeString(timeStringBuff);

    // Print received packet
    Serial.print("Received packet '");
    while (LoRa.available()) {
      Serial.print((char)LoRa.read());
    }
    Serial.print("' with RSSI ");

    // Print RSSI of packet
    int s = LoRa.packetRssi();
    Serial.println(s);
    Serial.print("Received packet at ");
    Serial.print(receiveTimeString);
    Serial.print(" - RSSI: ");
    Serial.println(s);

    // Store RSSI value
    sstrength[ind] = s;
    ind = (ind + 1) % numReadings;
  }
}

