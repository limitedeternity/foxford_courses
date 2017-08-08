from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException
from os.path import abspath, join, exists
from shutil import move
from os import unlink
from time import sleep
from . import element_screenshot


def filename(num):
    if num == 0:
        return 'mp4.mp4'

    else:
        return 'mp4 (' + str(num) + ').mp4'


def homework_download(driver, course_name, main_window):
    driver.get('file:///' + abspath(course_name + '_homework.html'))
    links = driver.find_elements_by_tag_name("a")
    print('\n')

    for num, link in enumerate(links):
        try:
            xname = str(links[num].text)
            print(xname + '. \nЗагрузка запущена.')

            driver.execute_script('window.open(arguments[0], "_blank");', link)
            windows = driver.window_handles
            driver.switch_to.window(windows[1])
            sleep(1)

            wrapper = driver.find_element_by_xpath("(//div[@class='custom-scroll '])[2]/../..")
            content = driver.find_element_by_xpath("(//div[@class='content-wrapper'])[2]")
            content_content = driver.find_element_by_xpath("(//div[@class='content-wrapper'])[2]/*[1]")
            wrapper_orig = driver.execute_script("return arguments[0].innerHTML;", wrapper)

            driver.execute_script("arguments[0].setAttribute('style', '');", content)
            driver.execute_script("arguments[0].setAttribute('style', '');", content_content)
            driver.execute_script("arguments[0].innerHTML = arguments[1];", wrapper, content.get_attribute("outerHTML"))

            element_screenshot(driver, xname, "_nil")
            sleep(1)
            driver.execute_script("arguments[0].innerHTML = arguments[1]", wrapper, wrapper_orig)
            sleep(1)

            try:
                driver.find_element_by_xpath("//a[contains(text(), 'Сдаюсь!')]").click()
                sleep(1)
                driver.find_element_by_xpath("//div[contains(text(), 'Да')]").click()
                sleep(1)

                driver.get(driver.current_url)

                wrapper = driver.find_element_by_xpath("(//div[@class='custom-scroll '])[2]/../..")
                content = driver.find_element_by_xpath("(//div[@class='content-wrapper'])[2]")
                content_content = driver.find_element_by_xpath("(//div[@class='content-wrapper'])[2]/*[1]")
                wrapper_orig = driver.execute_script("return arguments[0].innerHTML;", wrapper)

                driver.execute_script("arguments[0].setAttribute('style', '');", content)
                driver.execute_script("arguments[0].setAttribute('style', '');", content_content)
                driver.execute_script("arguments[0].innerHTML = arguments[1];", wrapper, content.get_attribute("outerHTML"))

                element_screenshot(driver, xname, "_solved")
                sleep(1)
                driver.execute_script("arguments[0].innerHTML = arguments[1]", wrapper, wrapper_orig)
                sleep(1)

            except NoSuchElementException:
                print("ДЗ уже решено.")

            print("ДЗ получено.")
            driver.execute_script('window.close();')
            driver.switch_to.window(main_window)
            sleep(1)

        except ElementNotVisibleException:
            print("Элемент не виден.")
            continue

        print('Загрузка завершена.')
        print('---\n')

    print('\n---\n')
    unlink(join(abspath("."), course_name + '_homework.html'))


def video_download(driver, course_name):
    driver.get('file:///' + abspath(course_name + '_videos.html'))
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
    unlink(join(abspath("."), course_name + '_videos.html'))
