import pyaudio
import socket
import time
# 音頻流參數
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

audio = pyaudio.PyAudio()

# 開啟麥克風錄音
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

# 創建socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("0.0.0.0", 5005))  # 確保替換成接收方的正確IP地址和端口
while True:
    data = stream.read(CHUNK, exception_on_overflow = False)
    s.sendall(data)
    # time.sleep(1)

# 關閉串流和socket
stream.stop_stream()
stream.close()
audio.terminate()
s.close()
