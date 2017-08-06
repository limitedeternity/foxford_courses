from selenium.common.exceptions import ElementNotVisibleException
from os.path import abspath, join, exists
from shutil import move
from os import unlink
from time import sleep


def filename(num):
    if num == 0:
        return 'mp4.mp4'

    else:
        return 'mp4 (' + str(num) + ').mp4'


def download(driver):
    driver.get('file://' + abspath('links.html'))
    links = driver.find_elements_by_tag_name("a")
    print('\n')

    for num, link in enumerate(links):
        try:
            link.click()
            print(str(links[num].text) + '. \nЗагрузка запущена.')

        except ElementNotVisibleException:
            print("Элемент не виден.")
            continue

        notloaded = True
        while notloaded:
            if exists(join(abspath("."), filename(num))):
                notloaded = False

            sleep(1)

        if exists(join(abspath("."), str(links[num].text) + ".mp4")):
            unlink(join(abspath("."), str(links[num].text) + ".mp4"))

        move(join(abspath("."), filename(num)), join(abspath("."), str(links[num].text) + ".mp4"))
        print('Загрузка завершена.')
        print('---\n')

    print('\n---\n')
