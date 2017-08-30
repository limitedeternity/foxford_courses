# -*- coding: utf-8 -*-

'''Imports'''

from os import chdir, getcwd, environ
from os.path import dirname, abspath
from sys import exit, platform
from subprocess import call
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
    print("1. Извлечь ВСЕ")
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

        if platform.startswith('win'):
            chdir(environ.get("WINDIR"))
            call("subst X: /d")

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

    while True:
        try:
            # Show login page or dashboard
            login_to_foxford(driver)
            cls()
            print("(Помни, что если хочешь пропустить загрузку чего-либо, кроме видео, жми Ctrl + C. Во время загрузки.)")
            print("Выбирай курс.")

            # Wait until user navigates to URL matching regex
            while not match(r"^((https?):\/\/)(foxford\.ru\/)(courses\/)(\d{3})(\/?)$", driver.current_url):
                sleep(1)

            cls()
            operator(driver, driver.current_url)
            sleep(1)
            input('Готово. Чтобы скачать еще курс, нажми Enter. Чтобы вернуться к меню, нажми Ctrl + C.\n')

        except KeyboardInterrupt:
            # On 'Ctrl + C' return to menu.
            selector()


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

    while True:
        try:
            # Show login page or dashboard
            login_to_foxford(driver)
            cls()
            print("Выбирай курс.")

            # Wait until user navigates to URL matching regex
            while not match(r"^((https?):\/\/)(foxford\.ru\/)(courses\/)(\d{3})(\/?)$", driver.current_url):
                sleep(1)

            cls()
            operator_shifted(driver, driver.current_url, 0)
            sleep(1)
            input('Готово. Чтобы скачать еще курс, нажми Enter. Чтобы вернуться к меню, нажми Ctrl + C.\n')

        except KeyboardInterrupt:
            # On 'Ctrl + C' return to menu.
            selector()


if __name__ == "__main__":

    # Small setup for paths
    chdir(dirname(abspath(__file__)))

    if platform.startswith('win'):
        if getcwd() != "X:\\":
            call('subst X: "."')
            sleep(1)
            chdir("X:\\")

    # Startup
    selector()
