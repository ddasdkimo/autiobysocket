import tkinter as tk
from tkinter import simpledialog
import pyaudio
import socket
import threading
import audioop
import configparser
import os
import sys

# 音頻流參數
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

# 設置檔案名稱
SETTINGS_FILE = "settings.ini"

def update_status(message, gui_mode=True):
    if gui_mode:
        status_label.config(text=message)
        root.update()
    else:
        print(message)

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

def stream_audio(ip, port, threshold, gui_mode=True):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.connect((ip, port))
        update_status("已連線到伺服器", gui_mode)
    except Exception as e:
        update_status(f"連線失敗: {e}", gui_mode)
        return

    while running:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            rms = audioop.rms(data, 2)
            if gui_mode:
                rms_label.config(text=f"音量 RMS 值: {rms}")
                root.update()
            if rms > threshold:
                print("已發送 音量 RMS 值: ", rms)
                s.sendall(data)
            else:
                print("不發送 音量 RMS 值: ", rms)
        except Exception as e:
            update_status(f"發生錯誤: {e}", gui_mode)
            return
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    s.close()
    update_status("連線已結束", gui_mode)

def main():
    settings = load_settings()
    if settings[0] == "0.0.0.0":  # 這表示沒有現有設置
        ip = input("輸入 IP 地址: ")
        port = int(input("輸入端口: "))
        threshold = int(input("輸入 RMS 閾值: "))
        save_settings(ip, port, threshold)
    else:
        print(f"使用現有設定: IP={settings[0]}, Port={settings[1]}, Threshold={settings[2]}")
    global running
    running = True
    stream_audio(settings[0], settings[1], settings[2], gui_mode=False)

if __name__ == "__main__":
    main()
