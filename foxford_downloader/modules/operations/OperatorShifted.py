from time import sleep
from . import generate_html_file, download
from selenium.common.exceptions import ElementNotVisibleException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from sys import exit


def operator_shifted(driver, course_link):
    lesson_name = ''
    course_name = ''
    main_window = driver.current_window_handle
    download_links = {}

    driver.get(course_link)
    print('\n')

    try:
        course_name = driver.find_element_by_class_name("course_info_title").text

    except ElementNotVisibleException:
        print("Элемент не виден.")
        sleep(1)
        pass

    print(course_name)

    try:
        driver.find_element_by_class_name("lesson active")
        driver.execute_script("document.getElementsByClassName('lesson active')[0].classList.remove('active');")

    except NoSuchElementException:
        pass

    sleep(0.5)
    lesson_links = driver.find_elements_by_class_name("lesson")
    print('\n---\n')

    for i in range(len(lesson_links) - 1):
        try:
            ActionChains(driver).move_to_element(lesson_links[i]).click(lesson_links[i]).perform()
            sleep(1)

        except ElementNotVisibleException:
            print("Элемент не виден.")
            sleep(1)
            continue

        except StaleElementReferenceException:
            print('Ошибка, связанная с большой задержкой ответа. Попробуй еще раз.')
            sleep(1)
            continue

        try:
            lesson_name = driver.find_element_by_class_name("lesson_content").find_element_by_tag_name('h2').text
            print(lesson_name)

        except ElementNotVisibleException:
            print("Элемент не виден.")
            sleep(1)
            continue

        except StaleElementReferenceException:
            print("Название не будет выведено автоматически.")
            continue

        try:
            webinar_link = driver.find_element_by_xpath("//i[@class='fxf_icon_small fxf_icon_video_blue']/..")
            if webinar_link is not None and webinar_link.get_attribute("class") != 'disabled':

                driver.execute_script('window.open("{}", "_blank");'.format(webinar_link.get_attribute("href")))

                windows = driver.window_handles
                driver.switch_to.window(windows[1])
                sleep(1)

                html_escape_table = {
                    "&": "&amp;",
                    '"': "&quot;",
                    "'": "&apos;",
                    ">": "&gt;",
                    "<": "&lt;",
                }

                try:
                    download_links[lesson_name] = driver.find_element_by_class_name("vjs-tech").get_attribute("src")
                    print("Видео получено.")
                    sleep(1)

                except NoSuchElementException:
                    pass

                try:
                    video_link = "".join(html_escape_table.get(c, c) for c in driver.find_element_by_class_name("full_screen").find_element_by_tag_name("iframe").get_attribute("src"))
                    driver.execute_script('window.open("{}", "_self");'.format(video_link))
                    sleep(1)

                    download_links[lesson_name] = driver.find_element_by_class_name("vjs-tech").get_attribute("src")
                    print("Видео получено.")
                    sleep(1)

                except NoSuchElementException:
                    print('Что-то пошло не так. Закрой все прочие браузеры и после 3-4 повторных попыток сообщи разработчику о проблеме.')
                    sleep(1)
                    exit(0)

                driver.execute_script('window.close();')
                driver.switch_to.window(main_window)
                sleep(1)

            else:
                print('Видео не существует. Ссылка отключена, или просто не прописана.')
                print('Ничего не поделать, идем дальше.')
                sleep(1)

            print('---\n')

        except NoSuchElementException:
            print("Видео не обнаружено.")
            print("Идем дальше.")
            print('---\n')
            sleep(1)

    generate_html_file(course_name, download_links)
    print("Список видео сформирован. Скачиваю...")
    print('---\n')
    download(driver)
