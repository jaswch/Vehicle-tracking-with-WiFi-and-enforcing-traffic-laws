/*
  * This code is for the vehicle for the project "Vehicle Tracking System".
  * It scans for two specific Wi-Fi networks: a hotspot and a beacon.
  * It retrieves the RSSI (signal strength) of these networks and sends the data
  * along with the vehicle's MAC address to a server running on a Raspberry Pi.
  * The server is expected to be listening on a specific IP address and port.
  * The vehicle's MAC address is also included in the data sent to the server.
  * The code is designed to run on an ESP8266 microcontroller.
  * No aditional circuit is required
   
   By Jaswanth Venkata Sai Chennu
   On 18 / 07 / 2025
*/
#include <Arduino.h>
#include <ESP8266WiFi.h>

// --- Configuration (EDIT THESE) ---
const char* hotspot_ssid = "Beacon_B";
const char* hotspot_password = "Hkdpwd@603";
const char* beacon_ssid = "Beacon_A";

// The IP address of your Raspberry Pi on the hotspot network.
// You will get this when you run the server script on the Pi.
const char* serverIP = "192.168.x.x"; 
const int serverPort = 9999;

String vehicleMAC;


// Function to send data to the server
void sendDataToServer(int rssi1, int rssi2) {
  // Connect to the Wi-Fi hotspot
  WiFi.begin(hotspot_ssid, hotspot_password);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  // If the vehicle is connected to the hotspot then connect to the server and send the data
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    if (client.connect(serverIP, serverPort)) {
      Serial.println("Connected to server.");
      // Send the mac address of the vehicle and the signal strength of the 2 APs
      String data = vehicleMAC + "," + String(rssi1) + "," + String(rssi2);
      
      // Send the data
      client.println(data);
      Serial.println("Data sent: " + data);
      client.stop();
    } else {
      Serial.println("Server connection failed.");
    }
  } else {
    Serial.println("Wi-Fi connection failed.");
  }
  WiFi.disconnect();
}

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA); // Set to client/station mode
  vehicleMAC = WiFi.macAddress();
  Serial.print("Vehicle MAC Address: ");
  Serial.println(vehicleMAC);
}

void loop() {
  Serial.println("Scanning for networks...");
  int network_count = WiFi.scanNetworks();

  int rssi_hotspot = -100; // Default "not found" value
  int rssi_beacon = -100;

  for (int i = 0; i < network_count; ++i) {
    String current_ssid = WiFi.SSID(i);
    if (current_ssid.equals(hotspot_ssid)) {
      rssi_hotspot = WiFi.RSSI(i);
    } else if (current_ssid.equals(beacon_ssid)) {
      rssi_beacon = WiFi.RSSI(i);
    }
  }
  
  Serial.printf("Found RSSI -> Hotspot: %d, Beacon: %d\n", rssi_hotspot, rssi_beacon);

  // Send the collected data to the server
  sendDataToServer(rssi_hotspot, rssi_beacon);

  delay(2000); // Wait 2 seconds before next scan
}

