# -*- coding: utf-8 -*-

from os import chdir, unlink
from os.path import dirname, abspath, exists, join
from sys import exit
from time import sleep
from re import match

from selenium import webdriver
from webbrowser import open
from selenium.webdriver.chrome.options import Options

from modules.common import cls, shutdown_chrome, login_to_foxford, system_platform

from modules.operations import operator


def selector():
    shutdown_chrome()
    cls()
    print("\n-------------------------------")
    print("1. Извлечь данные")
    print("2. Перейти в репозиторий")
    print("0. Выйти")
    print("-------------------------------\n")

    mode = input("Выбирай: ")
    sleep(0.5)

    if mode == '1':
        downloader()

    elif mode == '2':
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
    prefs = {"download.default_directory": abspath(".")}
    option.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=driver_location, chrome_options=option)
    driver.implicitly_wait(0.1)

    login_to_foxford(driver)

    while True:
        try:
            cls()
            course_link = input("Вставь ссылку на курс сюда: ")

            if exists(join(abspath('.'), 'links.html')):
                unlink(join(abspath('.'), 'links.html')

            else:
                pass

            if match(r"^((https?):\/\/)(foxford\.ru\/)(courses\/)(\d{3})(\/?)$", course_link):
                operator(driver, course_link)
                input('Готово. Чтобы скачать еще курс, нажми Enter. Чтобы вернуться к меню, нажми Ctrl + C.\n')

            else:
                print('Ссылка должна быть такой: https://foxford.ru/courses/xxx, где xxx - 3 цифры курса.')

        except KeyboardInterrupt:
            if exists(join(abspath('.'), 'links.html'):
                unlink(join(abspath('.'), 'links.html')

            else:
                pass

            selector()


if __name__ == "__main__":
    chdir(dirname(abspath(__file__)))
    selector()
