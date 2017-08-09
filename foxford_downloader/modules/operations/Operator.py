from time import sleep
from . import theory_html_gen, video_html_gen, homework_html_gen, theory_download, video_download, homework_download
from selenium.common.exceptions import ElementNotVisibleException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from sys import exit


def operator(driver, course_link):
    lesson_name = ''
    course_name = ''
    task_name = ''
    main_window = driver.current_window_handle
    theoretic_data = {}
    download_links = {}
    homework_links = {}

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

    try:
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

                    driver.execute_script('window.open(arguments[0], "_blank");', webinar_link.get_attribute("href"))

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
                        driver.execute_script('window.open(arguments[0], "_self");', video_link)
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
                    print('Видео отключено.')
                    print('Идем дальше.')
                    sleep(1)

                print('---\n')

            except NoSuchElementException:
                print("Видео не обнаружено.")
                print("Идем дальше.")
                print('---\n')
                sleep(1)

            try:
                homework_link = driver.find_element_by_xpath("//i[@class='fxf_icon_small fxf_icon_tasks_blue']/..")
                if homework_link is not None and homework_link.get_attribute("class") != 'disabled':

                    driver.execute_script('window.open(arguments[0], "_blank");', homework_link.get_attribute("href"))

                    windows = driver.window_handles
                    driver.switch_to.window(windows[1])
                    sleep(1)

                    try:
                        homework = driver.find_elements_by_xpath("(//div[@class='content-wrapper'])[1]/*[1]/*[position()>1]/*[1]/*[2]")

                        for i in range(len(homework)):
                            try:
                                ActionChains(driver).move_to_element(homework[i]).click(homework[i]).perform()
                                sleep(2)
                                task_name = driver.find_element_by_xpath("(//div[@class='content-wrapper'])[2]/*[1]/*[1]/*[2]/*[1]").text
                                homework_links[task_name] = driver.current_url
                                print("ДЗ записано в очередь.")
                                sleep(1)

                            except ElementNotVisibleException:
                                print("Элемент не виден.")
                                print('---\n')
                                sleep(1)

                            except StaleElementReferenceException:
                                print('Ошибка, связанная с большой задержкой ответа. Попробуй еще раз.')
                                print('---\n')
                                sleep(1)

                            except NoSuchElementException:
                                print('Что-то не так.')
                                print('---\n')
                                sleep(1)

                        print('---\n')

                    except NoSuchElementException:
                        print('Произошла ошибка.')
                        print('---\n')
                        sleep(1)

                    except IndexError:
                        print('Кажется, ДЗ не оплачено.')
                        print('---\n')
                        sleep(1)

                    driver.execute_script('window.close();')
                    driver.switch_to.window(main_window)
                    sleep(1)

                else:
                    print('ДЗ отключено.')
                    print('Идем дальше.')
                    print('---\n')
                    sleep(1)

            except NoSuchElementException:
                print("ДЗ не обнаружено.")
                print("Ищу теорию.")
                print('---\n')
                sleep(1)

            try:
                theory_link = driver.find_element_by_xpath("//i[@class='fxf_icon_small fxf_icon_conspects_blue']/..")
                if theory_link is not None and theory_link.get_attribute("class") != 'disabled':

                    driver.execute_script('window.open(arguments[0], "_blank");', theory_link.get_attribute("href"))

                    windows = driver.window_handles
                    driver.switch_to.window(windows[1])
                    sleep(1)

                    try:
                        theory_navigator = driver.find_elements_by_xpath("(//ul[@class='page_menu_list block_rounded_shadow'])[1]/*[position()>1]")

                        for i in range(len(theory_navigator)):
                            try:
                                ActionChains(driver).move_to_element(theory_navigator[i]).click(theory_navigator[i]).perform()
                                sleep(2)

                            except ElementNotVisibleException:
                                print("Элемент не виден.")
                                sleep(1)
                                continue

                            except StaleElementReferenceException:
                                print('Ошибка, связанная с большой задержкой ответа. Попробуй еще раз.')
                                sleep(1)
                                continue

                            theory_name = driver.find_element_by_class_name("info").find_element_by_tag_name('h1').text
                            theoretic_data[theory_name] = driver.current_url

                        print("Теория сохранена.")
                        print('---\n')
                        sleep(1)

                    except NoSuchElementException:
                        print('Произошла ошибка.')
                        print('---\n')
                        sleep(1)

                    driver.execute_script('window.close();')
                    driver.switch_to.window(main_window)
                    sleep(1)

                else:
                    print('Теория отключена.')
                    print('Идем дальше.')
                    print('---\n')
                    sleep(1)

            except NoSuchElementException:
                print("Теории не обнаружено.")
                print("Идем дальше.")
                print('---\n')
                sleep(1)

    except Exception:
        pass

    if len(theoretic_data.keys()) != 0:
        theory_html_gen(course_name, theoretic_data)
        print("Список теории сформирован. Обрабатываю...")
        print('---\n')
        theory_download(driver, course_name)
        sleep(1)

    if len(homework_links.keys()) != 0:
        homework_html_gen(course_name, homework_links)
        print("Список ДЗ сформирован. Скачиваю...")
        print('---\n')
        homework_download(driver, course_name)
        sleep(1)

    if len(download_links.keys()) != 0:
        video_html_gen(course_name, download_links)
        print("Список видео сформирован. Скачиваю...")
        print('---\n')
        video_download(driver, course_name)
        sleep(1)
