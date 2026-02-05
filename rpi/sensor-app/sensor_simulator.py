#!/usr/bin/env python3
"""
IoT Sensor Simulator
Simulates temperature, humidity, and motion sensors on a Raspberry Pi
Logs data in JSON format for easy ingestion into ELK stack
"""

import json
import logging
import random
import time
import os
from datetime import datetime

# Configure JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

class SensorSimulator:
    def __init__(self, node_id):
        self.node_id = node_id
        self.temp_base = random.uniform(18.0, 24.0)
        self.humidity_base = random.uniform(40.0, 60.0)
        self.motion_probability = 0.1

    def read_temperature(self):
        """Simulate temperature sensor (°C) with realistic drift"""
        drift = random.gauss(0, 0.5)
        temp = self.temp_base + drift
        # Simulate occasional spikes
        if random.random() < 0.05:
            temp += random.uniform(2, 5)
        return round(temp, 2)

    def read_humidity(self):
        """Simulate humidity sensor (%) with realistic drift"""
        drift = random.gauss(0, 2)
        humidity = self.humidity_base + drift
        return round(max(0, min(100, humidity)), 2)

    def read_motion(self):
        """Simulate PIR motion sensor"""
        return random.random() < self.motion_probability

    def log_sensor_data(self):
        """Read all sensors and log as structured JSON"""
        temp = self.read_temperature()
        humidity = self.read_humidity()
        motion = self.read_motion()

        # Create structured log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "node_id": self.node_id,
            "sensor_type": "environment",
            "metrics": {
                "temperature_celsius": temp,
                "humidity_percent": humidity,
                "motion_detected": motion
            },
            "status": "normal" if 15 <= temp <= 30 else "warning",
            "level": "info"
        }

        # Check for alerts
        if temp > 28:
            log_entry["level"] = "warning"
            log_entry["alert"] = "High temperature detected"
        elif temp < 16:
            log_entry["level"] = "warning"
            log_entry["alert"] = "Low temperature detected"

        if humidity > 70:
            log_entry["level"] = "warning"
            log_entry["alert"] = "High humidity detected"

        if motion:
            log_entry["event"] = "motion_detected"

        # Log as JSON
        logger.info(json.dumps(log_entry))

    def simulate_error(self):
        """Occasionally simulate sensor errors"""
        if random.random() < 0.02:  # 2% chance
            error_types = [
                "sensor_timeout",
                "sensor_disconnected",
                "invalid_reading",
                "calibration_error"
            ]
            error = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "node_id": self.node_id,
                "level": "error",
                "error_type": random.choice(error_types),
                "message": "Sensor communication failed, retrying..."
            }
            logger.error(json.dumps(error))

def main():
    node_id = os.getenv("NODE_ID", "rpi-unknown")
    interval = int(os.getenv("SAMPLE_INTERVAL", "10"))

    print(f"Starting sensor simulator for {node_id}")
    print(f"Sample interval: {interval} seconds")

    simulator = SensorSimulator(node_id)

    # Log startup
    startup_log = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "node_id": node_id,
        "level": "info",
        "event": "sensor_startup",
        "message": f"Sensor simulator started on {node_id}"
    }
    logger.info(json.dumps(startup_log))

    try:
        while True:
            simulator.log_sensor_data()
            simulator.simulate_error()
            time.sleep(interval)
    except KeyboardInterrupt:
        shutdown_log = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "node_id": node_id,
            "level": "info",
            "event": "sensor_shutdown",
            "message": f"Sensor simulator stopped on {node_id}"
        }
        logger.info(json.dumps(shutdown_log))

if __name__ == "__main__":
    main()
