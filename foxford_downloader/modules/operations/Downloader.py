from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from os.path import abspath, join, exists
from shutil import move
from os import unlink
from time import sleep
from . import theory_screenshot


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

    for i in range(len(links)):
        try:

            links[i].click()
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

            try:
                spoilers = driver.find_elements_by_class_name("toggle_element")
                for i in range(len(spoilers)):
                    ActionChains(driver).move_to_element(spoilers[i]).click(spoilers[i]).perform()

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
