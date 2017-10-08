from platform import machine
from sys import platform, exit
from time import sleep


def system_platform():
    '''Selects driver depending on platform'''

    if platform.startswith('win'):
        return 'modules/driver/win/chromedriver.exe'

    else:
        print("Not Windows.")
        sleep(1)
        exit(0)
