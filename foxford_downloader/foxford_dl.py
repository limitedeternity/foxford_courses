# -*- coding: utf-8 -*-

'''Imports'''

from os import chdir
from io import open as ioopen
from os.path import dirname, abspath, join
from sys import exit
from time import sleep
from re import match

from selenium import webdriver
from webbrowser import open as webopen
from selenium.webdriver.chrome.options import Options

from modules.common.CleanScreen import cls
from modules.common.FoxfordLogin import login_to_foxford
from modules.common.PlatformDetector import system_platform

from modules.operations.Operator import operator
from modules.operations.OperatorShifted import operator_shifted


def selector():

    '''Main menu'''

    cls()
    print("\n-------------------------------")
    print("1. Извлечь теорию И видео")
    print("2. Извлечь ТОЛЬКО видео")
    print("3. Навестить репозиторий автора")
    print("0. Выйти")
    print("-------------------------------\n")

    mode = input("Выбирай: ")
    sleep(0.5)

    if mode == '1':

        # Theory + video
        downloader()

    elif mode == '2':

        # Video-only
        downloader_shifted()

    elif mode == '3':

        # Visit repo
        cls()
        webopen("https://github.com/limitedeternity/foxford_courses", new=2)
        exit(0)

    else:

        # Exit
        cls()
        sleep(1)
        exit(0)


def downloader():

    '''Downloader for theory + video'''

    # Setting up ChromeDriver
    driver_location = system_platform()
    option = Options()
    option.add_argument("user-data-dir=" + abspath("Data"))  # <--- Isolated user profile

    option.add_argument("--start-maximized")  # <--- Fullscreen

    prefs = {"download.default_directory": abspath(".")}
    option.add_experimental_option("prefs", prefs)  # <--- Set download directory

    driver = webdriver.Chrome(executable_path=driver_location, chrome_options=option)
    driver.implicitly_wait(0.1)  # <--- Implict wait for each element

    login_to_foxford(driver)

    # Waiting for links
    input("Загрузи ссылки на курсы в links.txt - одна ссылка на строку, затем нажми Enter.")

    # Read links
    with ioopen(join(abspath("."), "links.txt"), "r", encoding="utf-8") as links:
        lines = links.readlines()

    # Iterate over each link and download contents
    for i in range(len(lines)):
        lines[i] = lines[i].strip()

        if not match(r"^((https?):\/\/)(foxford\.ru\/)(courses\/)(\d{3})(\/?)$", lines[i]):
                cls()
                print("...")
                exit(0)

        else:
            cls()
            operator(driver, lines[i])
            sleep(2)

    # Restoring placeholder when finished
    with ioopen(join(abspath('.'), 'links.txt'), "w", encoding="utf-8") as ph:
        ph.write("<-- PLACEHOLDER [REPLACE ME] -->")


def downloader_shifted():

    '''Video-only downloader'''

    # Setting up ChromeDriver
    driver_location = system_platform()
    option = Options()
    option.add_argument("user-data-dir=" + abspath("Data"))  # <--- Isolated user profile

    prefs = {"download.default_directory": abspath(".")}
    option.add_experimental_option("prefs", prefs)  # <--- Set download directory

    driver = webdriver.Chrome(executable_path=driver_location, chrome_options=option)
    driver.implicitly_wait(0.1)  # <--- Implict wait for each element

    login_to_foxford(driver)

    # Waiting for links
    input("Загрузи ссылки на курсы в links.txt - одна ссылка на строку, затем нажми Enter.")

    # Read them
    with ioopen(join(abspath("."), "links.txt"), "r", encoding="utf-8") as links:
        lines = links.readlines()

    # Use Operator on each link
    for i in range(len(lines)):
        lines[i] = lines[i].strip()

        if not match(r"^((https?):\/\/)(foxford\.ru\/)(courses\/)(\d{3})(\/?)$", lines[i]):
                cls()
                print("...")
                exit(0)

        else:
            cls()
            operator_shifted(driver, lines[i], 0)  # <--- "0" means 0 skips. Read more in operations directory.
            sleep(2)

    # Restoring placeholder when finished
    with ioopen(join(abspath('.'), 'links.txt'), "w", encoding="utf-8") as ph:
        ph.write("<-- PLACEHOLDER [REPLACE ME] -->")


if __name__ == "__main__":

    # Small setup for paths
    chdir(dirname(abspath(__file__)))

    # Startup
    selector()
