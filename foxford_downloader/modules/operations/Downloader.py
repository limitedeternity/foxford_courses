from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from os.path import abspath, join, exists
from os import unlink
from shutil import move
from time import sleep
from .ElementScreenshot import theory_screenshot


def theory_download(driver, course_name):
    driver.get('file:///' + join(abspath("."), course_name + '_theory.html'))
    main_window = driver.current_window_handle
    links = driver.find_elements_by_tag_name("a")
    print('\n')

    for i in range(len(links)):
        try:

            ActionChains(driver).move_to_element(links[i]).click(links[i]).perform()
            windows = driver.window_handles
            driver.switch_to.window(windows[1])

            sleep(1)
            driver.find_element_by_xpath("(//ul[@class='page_menu_list block_rounded_shadow'])[1]/*[1]").click()
            sleep(1)

            lesson_name = driver.find_element_by_class_name("lesson_content").find_element_by_tag_name('h2').text
            sleep(1)

            driver.execute_script("window.history.go(-1)")
            sleep(1)

            info = driver.find_element_by_class_name("info").find_element_by_tag_name('h1').text
            sleep(1)

            if exists(join(abspath("."), str(lesson_name).replace('"', '') + "_" + str(info).replace('"', '') + ".png")):
                driver.execute_script('window.close();')
                driver.switch_to.window(main_window)
                continue

            else:
                pass

            try:
                spoilers = driver.find_elements_by_class_name("toggle_element")
                for i in range(len(spoilers)):
                    ActionChains(driver).move_to_element(spoilers[i]).click(spoilers[i]).perform()
                    sleep(1)

            except NoSuchElementException:
                pass

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


def video_download(driver, course_name, course_link):
    driver.get('file:///' + join(abspath("."), course_name + '_videos.html'))
    links = driver.find_elements_by_tag_name("a")
    print('\n')

    skips = 0
    for i in range(len(links)):
        try:
            if exists(join(abspath("."), str(links[i].text) + ".mp4")):
                skips += 1
                continue

            else:
                pass

            if skips > 0:
                unlink(join(abspath("."), course_name + '_videos.html'))
                from .OperatorShifted import operator_shifted
                operator_shifted(driver, course_link, skips)
                sleep(1)
                return True

            ActionChains(driver).move_to_element(links[i]).click(links[i]).perform()
            print(str(links[i].text) + '. \nЗагрузка запущена.')

        except ElementNotVisibleException:
            print("Элемент не виден.")
            continue

        notloaded = True
        while notloaded:
            if exists(join(abspath("."), 'mp4.mp4')):
                notloaded = False

            sleep(1)

        move(join(abspath("."), 'mp4.mp4'), join(abspath("."), str(links[i].text) + ".mp4"))
        print('Загрузка завершена.')
        print('---\n')

    print('\n---\n')
