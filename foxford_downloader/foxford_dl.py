# -*- coding: utf-8 -*-

from os import chdir
from os.path import dirname, abspath
from sys import exit
from time import sleep
from re import match

from selenium import webdriver
from webbrowser import open
from selenium.webdriver.chrome.options import Options

from modules.common import cls, shutdown_chrome, login_to_foxford, system_platform

from modules.operations import operator, operator_shifted


def selector():
    shutdown_chrome()
    cls()
    print("\n-------------------------------")
    print("1. Извлечь ВСЕ данные /beta/")
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

    while True:
        try:
            cls()
            print("Выбирай курс.")

            while not match(r"^((https?):\/\/)(foxford\.ru\/)(courses\/)(\d{3})(\/?)$", driver.current_url):
                sleep(1)

            cls()
            operator(driver, driver.current_url)
            input('Готово. Чтобы скачать еще курс, нажми Enter. Чтобы вернуться к меню, нажми Ctrl + C.\n')

        except KeyboardInterrupt:

            selector()


def downloader_shifted():

    driver_location = system_platform()
    option = Options()
    option.add_argument("user-data-dir=" + abspath("Data"))
    prefs = {"download.default_directory": abspath(".")}
    option.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=driver_location, chrome_options=option)
    driver.implicitly_wait(0.1)

    login_to_foxford(driver)

    while True:
        try:
            cls()
            print("Выбирай курс.")

            while not match(r"^((https?):\/\/)(foxford\.ru\/)(courses\/)(\d{3})(\/?)$", driver.current_url):
                sleep(1)

            cls()
            operator_shifted(driver, driver.current_url)
            input('Готово. Чтобы скачать еще курс, нажми Enter. Чтобы вернуться к меню, нажми Ctrl + C.\n')

        except KeyboardInterrupt:

            selector()


if __name__ == "__main__":
    chdir(dirname(abspath(__file__)))
    selector()
