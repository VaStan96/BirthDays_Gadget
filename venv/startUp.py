import sys
import os
import shutil

def TurnOnStartUp():
    path = sys.argv[0]
    path = path.replace('/', '\\')
    file_name = path.split('\\')[-1]
    user_name = os.getenv('username')
    startup_path = f'C:\\Users\\{user_name}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\\'

    files = os.listdir(startup_path)
    if file_name not in files:
        shutil.copy(path, startup_path) # Copy .exe in dir StartUp


def TurnOffStartUp():
    path = sys.argv[0]
    path = path.replace('/', '\\')
    file_name = path.split('\\')[-1]
    user_name = os.getenv('username')
    startup_path = f'C:\\Users\\{user_name}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\\'

    files = os.listdir(startup_path)
    if file_name in files:
        os.remove(f'{startup_path+file_name}') # Delete .exe in dir StartUp
