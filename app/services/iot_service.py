from datetime import datetime
import random
import time

# Global State
sensor_data = {
    "temperature": 25.0,
    "gas_level": 10.0,
    "fire_class": "None",
    "image_url": "https://placeholder.com/safe.png",
    "alert_status": False,
    "humidity": 50.0,
    "last_updated": datetime.now().isoformat(),
    "device_id": "waiting_for_iot"
}

def update_sensor_data(temp, humidity, gas, device_id, alert_flag, fire_class="None"):
    global sensor_data
    sensor_data['temperature'] = temp
    sensor_data['humidity'] = humidity
    sensor_data['gas_level'] = gas
    sensor_data['device_id'] = device_id
    sensor_data['last_updated'] = datetime.now().isoformat()
    
    if alert_flag:
        sensor_data['alert_status'] = True
        sensor_data['fire_class'] = fire_class
    else:
        sensor_data['alert_status'] = False
        sensor_data['fire_class'] = "None"

def reset_alarm():
    global sensor_data
    sensor_data["alert_status"] = False
    sensor_data["fire_class"] = "None"
