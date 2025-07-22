/* 
  * Just an empty beacon which broadcasts a WiFi network to determine the vehicle location
  * No circuit required
  By Jaswanth Venkata Sai Chennu
  On 18 / 07 / 2025
*/

#include <WiFi.h>
const char* ssid = "Beacon_A";

void setup() {
  Serial.begin(115200);
  delay(10);
  // setup WiFi access point
  Serial.print("Setting up Access Point: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid);
  // Print the IP address
  Serial.print("AP IP address: ");
  Serial.println(WiFi.softAPIP());
}

void loop() {
  // Eat 5 star do nothing :)
  delay(5000);
}
