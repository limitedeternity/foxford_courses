from time import sleep
from . import element_screenshot, theory_html_gen, generate_html_file, download
from selenium.common.exceptions import ElementNotVisibleException, StaleElementReferenceException, NoSuchElementException
from sys import exit


def operator(driver, course_link):
    lesson_name = ''
    course_name = ''
    main_window = driver.current_window_handle
    theoretic_data = {}
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
            lesson_links[i].click()
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

        try:
            homework_link = driver.find_element_by_xpath("//i[@class='fxf_icon_small fxf_icon_tasks_blue']/..")
            if homework_link is not None and homework_link.get_attribute("class") != 'disabled':

                driver.execute_script('window.open("{}", "_blank");'.format(homework_link.get_attribute("href")))

                windows = driver.window_handles
                driver.switch_to.window(windows[1])
                sleep(1)

                try:
                    homework = driver.find_elements_by_xpath("(//div[@class='content-wrapper'])[1]/*[1]/*[position()>1]/*[1]/*[2]")
                    try:
                        homework[0].click()

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

                    for i in range(len(homework)):
                        wrapper = driver.find_elements_by_xpath("(//div[@class='custom-scroll '])[2]/../..")[0]
                        content = driver.find_elements_by_xpath("(//div[@class='content-wrapper'])[2]")[0]
                        content_content = driver.find_elements_by_xpath("(//div[@class='content-wrapper'])[2]/*[1]")[0]
                        wrapper_orig = driver.execute_script("return arguments[0].innerHTML;", wrapper)

                        driver.execute_script("arguments[0].setAttribute('style', '');", content)
                        driver.execute_script("arguments[0].setAttribute('style', '');", content_content)
                        driver.execute_script("arguments[0].innerHTML = arguments[1];", wrapper, content.get_attribute("outerHTML"))

                        element_screenshot(driver, lesson_name, i, "0")
                        print("ДЗ без ответов получено.\n")
                        driver.execute_script("arguments[0].innerHTML = arguments[1]", wrapper, wrapper_orig)
                        sleep(1)

                        try:
                            driver.find_element_by_xpath("//a[contains(text(), 'Сдаюсь!')]").click()
                            sleep(1)
                            driver.find_element_by_xpath("//div[contains(text(), 'Да')]").click()
                            sleep(1)

                            driver.get(driver.current_url)

                            wrapper = driver.find_elements_by_xpath("(//div[@class='custom-scroll '])[2]/../..")[0]
                            content = driver.find_elements_by_xpath("(//div[@class='content-wrapper'])[2]")[0]
                            content_content = driver.find_elements_by_xpath("(//div[@class='content-wrapper'])[2]/*[1]")[0]
                            wrapper_orig = driver.execute_script("return arguments[0].innerHTML;", wrapper)

                            driver.execute_script("arguments[0].setAttribute('style', '');", content)
                            driver.execute_script("arguments[0].setAttribute('style', '');", content_content)
                            driver.execute_script("arguments[0].innerHTML = arguments[1];", wrapper, content.get_attribute("outerHTML"))

                            element_screenshot(driver, lesson_name, i, "1")
                            print("ДЗ с ответами получено.\n")
                            driver.execute_script("arguments[0].innerHTML = arguments[1]", wrapper, wrapper_orig)
                            sleep(1)

                        except NoSuchElementException:
                            print("ДЗ уже решено.")
                            pass

                        print('---\n')

                        next_url = driver.execute_script("return location.href.replace(location.href.substr(location.href.lastIndexOf('/')+1), (Number(location.href.substr(location.href.lastIndexOf('/')+1))+1).toString());")
                        driver.get(next_url)
                        sleep(2)

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
                sleep(1)

        except NoSuchElementException:
            print("ДЗ не обнаружено.")
            print("Ищу теорию.")
            print('---\n')
            sleep(1)

        try:
            theory_link = driver.find_element_by_xpath("//i[@class='fxf_icon_small fxf_icon_conspects_blue']/..")
            if theory_link is not None and theory_link.get_attribute("class") != 'disabled':

                driver.execute_script('window.open("{}", "_blank");'.format(theory_link.get_attribute("href")))

                windows = driver.window_handles
                driver.switch_to.window(windows[1])
                sleep(1)

                try:
                    theory_navigator = driver.find_elements_by_xpath("(//ul[@class='page_menu_list block_rounded_shadow'])[1]/*[position()>1]")

                    for _ in range(len(theory_navigator)):
                        try:
                            theory_navigator[i].find_element_by_tag_name("a").click()
                            sleep(1)

                        except ElementNotVisibleException:
                            print("Элемент не виден.")
                            sleep(1)
                            continue

                        except StaleElementReferenceException:
                            print('Ошибка, связанная с большой задержкой ответа. Попробуй еще раз.')
                            sleep(1)
                            continue

                        theory = driver.find_element_by_class_name("page_content_main").find_elements_by_tag_name("a")

                        for link in theory:
                            theoretic_data[link.text] = link.get_attribute("href")

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

    theory_html_gen(theoretic_data, course_name)
    print("Список теории сформирован.")
    sleep(1)
    generate_html_file(course_name, download_links)
    print("Список видео сформирован. Скачиваю...")
    print('---\n')
    download(driver)
