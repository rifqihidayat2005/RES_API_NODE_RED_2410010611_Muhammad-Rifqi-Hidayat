import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime

# Konfigurasi MQTT
BROKER = "localhost"
PORT = 1883
TOPIC_SENSOR = "iot/sensor"
TOPIC_KONTROL = "iot/kontrol"

# Membuat client MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ESP32-Simulator")

try:
    # Menghubungkan ke broker Mosquitto
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    print("ESP32 Simulator berjalan... Ctrl+C untuk stop")

    while True:
        # Membuat data sensor secara acak
        data = {
            "suhu": round(random.uniform(25, 32), 1),
            "kelembaban": round(random.uniform(55, 80), 1),
            "timestamp": datetime.now().isoformat()
        }

        # Mengirim data ke MQTT
        client.publish(TOPIC_SENSOR, json.dumps(data))

        print(f"→ Publish: {data}")

        # Mengirim data setiap 3 detik
        time.sleep(3)

except KeyboardInterrupt:
    print("\nESP32 Simulator dihentikan.")

except Exception as e:
    print(f"Terjadi kesalahan: {e}")

finally:
    client.loop_stop()
    client.disconnect()
    print("Koneksi MQTT ditutup.")