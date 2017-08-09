from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException
from os.path import abspath, join, exists
from shutil import move
from os import unlink
from time import sleep
from . import homework_screenshot, theory_screenshot


def filename(num):
    if num == 0:
        return 'mp4.mp4'

    else:
        return 'mp4 (' + str(num) + ').mp4'


def theory_download(driver, course_name):
    driver.get('file:///' + abspath(course_name + '_theory.html'))
    main_window = driver.current_window_handle
    links = driver.find_elements_by_tag_name("a")
    print('\n')

    for num, link in enumerate(links):
        try:

            link.click()
            windows = driver.window_handles
            driver.switch_to.window(windows[1])

            sleep(1)
            driver.find_element_by_xpath("(//ul[@class='page_menu_list block_rounded_shadow'])[1]/*[1]").click()
            sleep(1)

            lesson_name = driver.find_element_by_class_name("lesson_content").find_element_by_tag_name('h2').text
            sleep(1)

            driver.execute_script('window.close();')
            driver.switch_to.window(main_window)
            sleep(1)

            link.click()
            windows = driver.window_handles
            driver.switch_to.window(windows[1])
            sleep(1)

            info = driver.find_element_by_class_name("info").find_element_by_tag_name('h1').text
            sleep(1)

            theory_screenshot(driver, lesson_name, info)
            sleep(1)

            print("Теория получена.")
            sleep(1)

        except ElementNotVisibleException:
            print("Элемент не виден.")

        except NoSuchElementException:
            print("Где-то что-то не так.")

        driver.execute_script('window.close();')
        driver.switch_to.window(main_window)
        print('---\n')

    print('\n---\n')


def homework_download(driver, course_name):
    driver.get('file:///' + abspath(course_name + '_homework.html'))
    main_window = driver.current_window_handle
    links = driver.find_elements_by_tag_name("a")
    print('\n')

    for num, link in enumerate(links):
        try:

            link.click()
            windows = driver.window_handles
            driver.switch_to.window(windows[1])

            sleep(1)
            driver.find_element_by_xpath("(//div[@class='content-wrapper'])[1]/*[1]/*[1]").click()
            sleep(1)

            lesson_name = driver.find_element_by_class_name("lesson_content").find_element_by_tag_name('h2').text
            sleep(1)

            driver.execute_script('window.close();')
            driver.switch_to.window(main_window)
            sleep(1)

            link.click()
            windows = driver.window_handles
            driver.switch_to.window(windows[1])
            sleep(1)

            task_name = driver.find_element_by_xpath("(//div[@class='content-wrapper'])[2]/*[1]/*[1]/*[2]/*[1]").text
            wrapper = driver.find_element_by_xpath("(//div[@class='custom-scroll '])[2]/../..")
            content = driver.find_element_by_xpath("(//div[@class='content-wrapper'])[2]")
            content_content = driver.find_element_by_xpath("(//div[@class='content-wrapper'])[2]/*[1]")
            wrapper_orig = driver.execute_script("return arguments[0].innerHTML;", wrapper)

            driver.execute_script("arguments[0].setAttribute('style', '');", content)
            driver.execute_script("arguments[0].setAttribute('style', '');", content_content)
            driver.execute_script("arguments[0].innerHTML = arguments[1];", wrapper, content.get_attribute("outerHTML"))
            sleep(1)

            homework_screenshot(driver, lesson_name, task_name, "0")
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
                sleep(1)

                homework_screenshot(driver, lesson_name, task_name, "1")
                sleep(1)
                driver.execute_script("arguments[0].innerHTML = arguments[1]", wrapper, wrapper_orig)
                sleep(1)

            except NoSuchElementException:
                print("ДЗ уже решено.")
                move(join(abspath("."), lesson_name + "_" + task_name + "_0" + ".png"), join(abspath("."), lesson_name + "_" + task_name + "_1" + ".png"))

            print("ДЗ получено.")
            sleep(1)

        except ElementNotVisibleException:
            print("Элемент не виден.")

        driver.execute_script('window.close();')
        driver.switch_to.window(main_window)
        print('---\n')

    print('\n---\n')


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
