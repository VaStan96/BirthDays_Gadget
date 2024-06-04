import sys
import os
from win32com.client import Dispatch

def TurnOnStartUp():
    path = sys.argv[0]
    path = path.replace('/', '\\')
    file_name = 'BirthDays_Gadget.lnk' #path.split('\\')[-1]
    user_name = os.getenv('username')
    startup_path = f'C:\\Users\\{user_name}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\\'

    files = os.listdir(startup_path)
    if file_name not in files:
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(startup_path+file_name)
        shortcut.Targetpath = path
        shortcut.WorkingDirectory = path[:path.rfind('\\')]
        shortcut.save()


def TurnOffStartUp():
    path = sys.argv[0]
    path = path.replace('/', '\\')
    file_name = 'BirthDays_Gadget.lnk' #path.split('\\')[-1]
    user_name = os.getenv('username')
    startup_path = f'C:\\Users\\{user_name}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\\'

    files = os.listdir(startup_path)
    if file_name in files:
        os.remove(f'{startup_path+file_name}') # Delete .lnk in dir StartUp
