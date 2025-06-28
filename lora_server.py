# lora_server.py
from flask import Flask, jsonify
import serial
import threading

app = Flask(__name__)
latest_pos = {"lat": 0.0, "lng": 0.0}

# 1. 시리얼 포트에서 아두이노로부터 GPS 데이터 읽기
def read_serial():
    global latest_pos
    ser = serial.Serial('COM3', 115200)  # 포트 번호는 환경에 맞게 수정
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("$GPRMC"):
            try:
                parts = line.split(',')
                if parts[2] == 'A':  # 유효한 GPS 데이터
                    lat_raw, lat_dir = parts[3], parts[4]
                    lng_raw, lng_dir = parts[5], parts[6]
                    lat = dmm_to_dd(lat_raw, lat_dir)
                    lng = dmm_to_dd(lng_raw, lng_dir)
                    latest_pos = {"lat": lat, "lng": lng}
                    print("위치 업데이트:", latest_pos)
            except:
                continue

def dmm_to_dd(raw, direction):
    deg_len = 2 if direction in ['N', 'S'] else 3
    degrees = float(raw[:deg_len])
    minutes = float(raw[deg_len:])
    result = degrees + minutes / 60
    if direction in ['S', 'W']:
        result *= -1
    return result

# 2. 위치 저장 API
@app.route('/pos')
def get_position():
    return jsonify(latest_pos)

# 3. 시리얼 스레드 실행 + 서버 실행
if __name__ == '__main__':
    t = threading.Thread(target=read_serial, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)
