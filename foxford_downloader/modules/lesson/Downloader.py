from selenium.common.exceptions import ElementNotVisibleException
from os.path import abspath
from time import sleep


def download(driver):
    driver.get('file://' + abspath('links.html'))
    links = driver.find_elements_by_tag_name("a")

    for num, link in enumerate(links):
        try:
            link.click()
            print('#' + str(num + 1) + '. Загрузка запущена.')

        except ElementNotVisibleException:
            print("Элемент не виден.")
            continue

        sleep(30)

    print('\n---\n')
