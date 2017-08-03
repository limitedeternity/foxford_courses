from platform import machine
from sys import platform, exit
from time import sleep
from . import cls


def system_platform():
    '''Selects driver depending on platform'''

    if platform.startswith('win'):
        return 'modules/driver/win/chromedriver.exe'
    elif platform.startswith('darwin'):
        return 'modules/driver/darwin/chromedriver'
    elif platform.startswith('linux'):
        if machine().endswith('64'):
            return 'modules/driver/linux/x64/chromedriver'
        else:
            return 'modules/driver/linux/x86/chromedriver'
    else:
        print("Поставь нормальную систему.")
        sleep(1)
        cls()
        exit(0)
