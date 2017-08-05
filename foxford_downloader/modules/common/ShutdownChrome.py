from subprocess import call
from sys import platform, exit
from time import sleep
from . import cls


def shutdown_chrome():
    '''Memory leak workaround'''

    if platform.startswith('win'):
            call('taskkill /F /IM chrome.exe', shell=True)

    elif platform.startswith('darwin'):
            call('pkill -a -i "Google Chrome"', shell=True)

    elif platform.startswith('linux'):
            call('kill -9 `ps -A |grep chrome| cut -d "?" -f1`', shell=True)

    else:
        print("Поставь нормальную систему.")
        sleep(1)
        cls()
        exit(0)
