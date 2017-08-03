# -*- coding: utf-8 -*-

from os import chdir, unlink
from os.path import dirname, abspath, isfile
from sys import exit
from time import sleep
from re import match

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from modules.common import cls, shutdown_chrome, login_to_foxford, system_platform

from modules.homework import homework_operator

from modules.lesson import lesson_operator


def selector():
    shutdown_chrome()
    cls()
    print("\n------------------------------")
    print("1. Сделать скриншот ДЗ")
    print("2. Скачать курс")
    print("0. Выйти")
    print("------------------------------\n")

    mode = input("Выбирай: ")
    sleep(0.5)

    if mode == '1':
        # homework_downloader()
        print('Пока сломано')
        sleep(1)
        exit(0)

    elif mode == '2':
        video_downloader()

    else:
        cls()
        sleep(1)
        exit(0)


def homework_downloader():

    driver_location = system_platform()
    option = Options()
    option.add_argument("user-data-dir=Chrome")
    driver = webdriver.Chrome(executable_path=driver_location, chrome_options=option)
    driver.implicitly_wait(0.1)

    login_to_foxford(driver)

    while True:
        try:
            cls()
            homework_link = input("Вставь ссылку на ДЗ сюда: ")
            homework_operator(driver, homework_link)
            input("Чтобы сохранить еще ДЗ, нажми Enter. Чтобы вернуться к меню, нажми Ctrl + C.\n")

        except KeyboardInterrupt:
            selector()


def video_downloader():

    driver_location = system_platform()
    option = Options()
    option.add_argument("user-data-dir=Chrome")
    option.add_extension('./download_manager.crx')
    driver = webdriver.Chrome(executable_path=driver_location, chrome_options=option)
    driver.implicitly_wait(0.1)

    login_to_foxford(driver)

    while True:
        try:
            cls()
            course_link = input("Вставь ссылку на курс сюда: ")

            if isfile('./links.html'):
                unlink('./links.html')

            else:
                pass

            if match(r"^((https?):\/\/)(foxford\.ru\/)(courses\/)(\d{3})(\/?)$", course_link):
                lesson_operator(driver, course_link)
                input('Готово. Чтобы скачать еще курс, нажми Enter. Чтобы вернуться к меню, нажми Ctrl + C.\n')

            else:
                print('Ссылка должна быть такой: https://foxford.ru/courses/xxx, где xxx - 3 цифры курса.')

        except KeyboardInterrupt:
            if isfile('./links.html'):
                unlink('./links.html')

            else:
                pass

            selector()


if __name__ == "__main__":
    chdir(dirname(abspath(__file__)))
    selector()
