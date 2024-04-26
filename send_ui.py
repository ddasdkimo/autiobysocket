# pyinstaller --onefile --windowed --hidden-import=module_name1 --hidden-import=module_name2 send_ui.py
# pyinstaller --onefile send_ui.py
# pyinstaller --onefile --windowed send_ui.py
import tkinter as tk
from tkinter import simpledialog
import pyaudio
import socket
import threading
import audioop
import configparser
import os

# 音頻流參數
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

# 設置檔案名稱
SETTINGS_FILE = "settings.ini"

def update_status(message):
    status_label.config(text=message)
    root.update()

def save_settings(ip, port, threshold):
    config = configparser.ConfigParser()
    config['DEFAULT'] = {
        'IP': ip,
        'Port': str(port),
        'Threshold': str(threshold)
    }
    with open(SETTINGS_FILE, 'w') as configfile:
        config.write(configfile)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        config = configparser.ConfigParser()
        config.read(SETTINGS_FILE)
        return (config['DEFAULT']['IP'], int(config['DEFAULT']['Port']), int(config['DEFAULT']['Threshold']))
    else:
        return ("0.0.0.0", 5005, 6000)  # 預設設置

def stream_audio(ip, port, threshold):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.connect((ip, port))
        update_status("已連線到伺服器")
    except Exception as e:
        update_status(f"連線失敗: {e}")
        return

    while running:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            rms = audioop.rms(data, 2)
            rms_label.config(text=f"音量 RMS 值: {rms}")
            root.update()
            if rms > threshold:
                print("已發送 音量 RMS 值: ", rms)
                s.sendall(data)
            else:
                print("不發送 音量 RMS 值: ", rms)
        except Exception as e:
            update_status(f"發生錯誤: {e}")
            return
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    s.close()
    update_status("連線已結束")

def start_streaming():
    global running
    ip = ip_entry.get()
    port = int(port_entry.get())
    threshold = int(threshold_entry.get())
    running = True
    save_settings(ip, port, threshold)  # 儲存設置
    threading.Thread(target=stream_audio, args=(ip, port, threshold)).start()

def stop_streaming():
    global running
    running = False

# 建立 GUI
root = tk.Tk()
root.title("音頻串流")
settings = load_settings()  # 載入設置

tk.Label(root, text="IP 地址:").pack()
ip_entry = tk.Entry(root)
ip_entry.pack()
ip_entry.insert(0, settings[0])

tk.Label(root, text="端口:").pack()
port_entry = tk.Entry(root)
port_entry.pack()
port_entry.insert(0, settings[1])

tk.Label(root, text="RMS 閾值:").pack()
threshold_entry = tk.Entry(root)
threshold_entry.pack()
threshold_entry.insert(0, settings[2])

start_button = tk.Button(root, text="開始錄音", command=start_streaming)
start_button.pack()

stop_button = tk.Button(root, text="停止錄音", command=stop_streaming)
stop_button.pack()

status_label = tk.Label(root, text="連線狀態: 未連線")
status_label.pack()

rms_label = tk.Label(root, text="音量 RMS 值: 未測量")
rms_label.pack()

root.mainloop()
