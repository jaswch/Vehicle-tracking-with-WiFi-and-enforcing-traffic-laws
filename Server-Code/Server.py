# Server for Vehicle Tracking and Traffic Violation Detection
# This server listens for vehicle data, calibrates RSSI fingerprints, and detects traffic violations.
# It uses a SQLite database to log violations and a JSON file to store fingerprints.
# By Jaswanth Venkata Sai Chennu, 18 / 07 / 2025
import socket
import json
import sqlite3
import os
from datetime import datetime

# --- Configuration ---
HOST = '0.0.0.0'  # Listen on all available network interfaces
PORT = 9999
FINGERPRINT_FILE = 'fingerprint_map_2ap.json'

def createDatabase():
    # This will create the database file in the same directory
    conn = sqlite3.connect('traffic_violations.db')
    cursor = conn.cursor()
    # Create the table to store violation records
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mac_address TEXT NOT NULL,
            violation_type TEXT NOT NULL,
            timestamp DATETIME NOT NULL
        )
    ''')
    print("✅ Database 'traffic_violations.db' created successfully.")
    conn.commit()
    conn.close()

# load fingerprints from JSON file
def load_fingerprints():
    if os.path.exists(FINGERPRINT_FILE):
        with open(FINGERPRINT_FILE, 'r') as f:
            return json.load(f)
    return {}

# save fingerprints to JSON file
def save_fingerprints(fingerprints):
    with open(FINGERPRINT_FILE, 'w') as f:
        json.dump(fingerprints, f, indent=4)
        
# find the closest location based on RSSI values
def find_closest_location(live_rssi, fingerprints):
    best_location = "Unknown"
    smallest_diff = float('inf')

    for location, stored_rssi in fingerprints.items():
        # Updated for 2 RSSI values
        diff = abs(live_rssi['rssi_hotspot'] - stored_rssi['rssi_hotspot']) + \
               abs(live_rssi['rssi_beacon'] - stored_rssi['rssi_beacon'])
        if diff < smallest_diff:
            smallest_diff = diff
            best_location = location
    return best_location

def log_violation(mac, violation_type):
    conn = sqlite3.connect('traffic_violations.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO violations (mac_address, violation_type, timestamp) VALUES (?, ?, ?)",
                   (mac, violation_type, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    print(f"🚨 VIOLATION! Vehicle: {mac}, Rule: {violation_type}")

# --- Main Application Modes ---
def run_calibration_mode(server_socket):
    print("\n--- Starting CALIBRATION Mode ---")
    fingerprints = load_fingerprints()
    
    while True:
        location_name = input("\nEnter location name (e.g., 'intersection') or 'done': ")
        if location_name.lower() == 'done':
            break

        print(f"Place vehicle at '{location_name}' and wait for data...")
        conn, addr = server_socket.accept()
        data = conn.recv(1024).decode().strip()
        conn.close()
        
        try:
            _, rssi1, rssi2 = data.split(',')
            rssi_data = {'rssi_hotspot': int(rssi1), 'rssi_beacon': int(rssi2)}
            fingerprints[location_name] = rssi_data
            save_fingerprints(fingerprints)
            print(f"✅ Fingerprint for '{location_name}' saved: {rssi_data}")
        except Exception as e:
            print(f"Error processing data: {e}")

def run_tracking_mode(server_socket):
    print("\n--- Starting TRACKING Mode ---")
    fingerprints = load_fingerprints()
    if not fingerprints:
        print("❌ Map is empty. Run calibration first.")
        return

    while True:
        conn, addr = server_socket.accept()
        data = conn.recv(1024).decode().strip()
        conn.close()
        
        try:
            mac, rssi1, rssi2 = data.split(',')
            live_rssi = {'rssi_hotspot': int(rssi1), 'rssi_beacon': int(rssi2)}
            
            location = find_closest_location(live_rssi, fingerprints)
            print(f"Vehicle {mac} is at location: {location}")

            # Simple Rule Check (can be expanded with traffic light state)
            if location == "intersection": # Example rule
                log_violation(mac, "Entered Intersection")
            if "wrong_lane" in location:
                log_violation(mac, "Wrong Lane")
        except Exception as e:
            print(f"Error processing data: {e}")

if __name__ == '__main__':
    # Get the Pi's IP address on the hotspot network to show the user
    my_ip = os.popen('hostname -I').read().strip()
    print("--- 🚦 Simple Vehicle Tracking Server ---")
    print(f"✅ Your Raspberry Pi's IP address is: {my_ip}")
    print("Please put this IP into the vehicle's Arduino code.")
    # create a new TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        
        mode = input("Select mode: [1] Calibrate, [2] Track or [3] Create Database: ")
        if mode == '1':
            run_calibration_mode(s)
        elif mode == '2':
            run_tracking_mode(s)
        elif mode == '3':
            createDatabase(s)
        else:
            print("Invalid choice.")
