import pyaudio
import socket
import logging

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')
# 音頻流參數
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
BUFFER_SIZE = 10  # 緩衝區大小，以CHUNK為單位

audio = pyaudio.PyAudio()

# 開啟播放
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, output=True,
                    frames_per_buffer=CHUNK)

# 創建socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 5005))
s.listen(1)
conn, addr = s.accept()

buffer = []
try:
    while True:
        data = conn.recv(CHUNK)
        buffer.append(data)
        if len(buffer) >= BUFFER_SIZE:
            for frame in buffer:
                stream.write(frame)
            buffer = []  # 清空緩衝區
except Exception as e:
    logging.error(f" 錯誤: {e}")

# 關閉串流
stream.stop_stream()
stream.close()
audio.terminate()
conn.close()
s.close()
