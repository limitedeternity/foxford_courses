# -*- coding: utf-8 -*-

from os import chdir
from io import open as ioopen
from os.path import dirname, abspath, join
from sys import exit
from time import sleep
from re import match

from selenium import webdriver
from webbrowser import open
from selenium.webdriver.chrome.options import Options

from modules.common.CleanScreen import cls
from modules.common.ShutdownChrome import shutdown_chrome
from modules.common.FoxfordLogin import login_to_foxford
from modules.common.PlatformDetector import system_platform

from modules.operations.Operator import operator
from modules.operations.OperatorShifted import operator_shifted


def selector():
    shutdown_chrome()
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
        downloader()

    elif mode == '2':
        downloader_shifted()

    elif mode == '3':
        cls()
        open("https://github.com/limitedeternity/foxford_courses", new=2)
        exit(0)

    else:
        cls()
        sleep(1)
        exit(0)


def downloader():

    driver_location = system_platform()
    option = Options()
    option.add_argument("user-data-dir=" + abspath("Data"))
    option.add_argument("--start-maximized")
    prefs = {"download.default_directory": abspath(".")}
    option.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=driver_location, chrome_options=option)
    driver.implicitly_wait(0.1)

    login_to_foxford(driver)
    input("Загрузи ссылки на курсы в links.txt - одна ссылка на строку, затем нажми Enter.")

    with ioopen(join(abspath("."), "links.txt"), "r", encoding="utf-8") as links:
        lines = links.readlines()

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


def downloader_shifted():

    driver_location = system_platform()
    option = Options()
    option.add_argument("user-data-dir=" + abspath("Data"))
    prefs = {"download.default_directory": abspath(".")}
    option.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=driver_location, chrome_options=option)
    driver.implicitly_wait(0.1)

    login_to_foxford(driver)
    input("Загрузи ссылки на курсы в links.txt - одна ссылка на строку, затем нажми Enter.")

    with ioopen(join(abspath("."), "links.txt"), "r", encoding="utf-8") as links:
        lines = links.readlines()

    for i in range(len(lines)):
        lines[i] = lines[i].strip()

        if not match(r"^((https?):\/\/)(foxford\.ru\/)(courses\/)(\d{3})(\/?)$", lines[i]):
                cls()
                print("...")
                exit(0)

        else:
            cls()
            operator_shifted(driver, lines[i], 0)
            sleep(2)


if __name__ == "__main__":
    chdir(dirname(abspath(__file__)))
    selector()
