'''Imports'''

from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from os.path import abspath, join, exists
from shutil import move
from time import sleep
from .ElementScreenshot import theory_screenshot


def theory_download(driver, course_name):
    '''Downloader for theory module'''

    driver.get('file:///' + join(abspath("."), course_name + '_theory.html'))  # <--- Getting HTML, generated with TheoryHTML.py, containing links

    main_window = driver.current_window_handle  # <--- Bind to tab with HTML file

    links = driver.find_elements_by_tag_name("a")  # <--- Making an array of links to iterate over them
    print('\n')

    # For each link...
    for i in range(len(links)):
        try:
            # If theory with this name already exists...
            if exists(join(abspath("."), str(links[i].text) + ".png")):
                # ...increase counter and go to another link
                continue

            # ...else go next
            else:
                pass

            # Setting filename still
            file = str(links[i].text) + ".png"

            ActionChains(driver).move_to_element(links[i]).click(links[i]).perform()  # <--- ...locate it using driver even if it's not visible and click it.

            windows = driver.window_handles  # <--- Enumerating all tabs, because link is opening in new tab (see TheoryHTML.py)

            driver.switch_to.window(windows[1])  # <--- Switching to tab with theory

            sleep(1)

            try:
                # If there are any spoilers, make an array of them...
                spoilers = driver.find_elements_by_class_name("toggle_content")

                # ...and make each of them visible.
                for i in range(len(spoilers)):
                    driver.execute_script("arguments[0].style.display = 'block';", spoilers[i])
                    sleep(1)

            # If none located, go next.
            except NoSuchElementException:
                pass

            # Screenshot theory area (see ElementScreenshot.py)
            theory_screenshot(driver, file)
            sleep(1)

            print("Теория получена.")
            sleep(1)

        except ElementNotVisibleException:
            print("Элемент не виден.")

        except NoSuchElementException:
            print("Где-то что-то не так.")

        # Return back to HTML
        driver.execute_script('window.close();')
        driver.switch_to.window(main_window)
        sleep(1)
        print('---\n')

    print('\n---\n')


def video_download(driver, course_name, course_link, html_repair=False):

    '''Video downloader module. html_repair specifies if download was interrupted.'''

    driver.get('file:///' + join(abspath("."), course_name + '_videos.html'))  # <--- Getting HTML, generated by VideoHTML.py.
    links = driver.find_elements_by_tag_name("a")  # <--- Making list of links, containing videos.
    print('\n')

    # Amount of videos to skip. Counter.
    skips = 0

    # Interate over links...
    for i in range(len(links)):
        try:
            # ...and check if file was already downloaded (exists with this filename)
            if exists(join(abspath("."), str(links[i].text) + ".mp4")):
                # If so, increase counter and go to another link
                skips += 1
                continue

            # Else go next
            else:
                pass

            # If there were videos to skip AND html_repair is specified by Operator.py...
            if skips > 0 and html_repair is True:

                # ...we need another list with ONLY videos. Giving skips parameter to OperatorShited.py function
                from .OperatorShifted import operator_shifted
                operator_shifted(driver, course_link, skips)
                sleep(1)

                # Finish video_download, when operator_shifted and new instance of video_download are finished their work
                return True

            # If html_repair is not specified, just download video after skips (if any)
            ActionChains(driver).move_to_element(links[i]).click(links[i]).perform()  # <--- Download locate and click, even if not visible
            print(str(links[i].text) + '. \nЗагрузка запущена.')

        except ElementNotVisibleException:
            print("Элемент не виден.")
            continue

        # Await for download finish. Based on fact that Chrome downloads video with name "mp4.mp4". But in some cases, Chrome uses "mp4".
        notloaded = True
        fname = None
        while notloaded:
            if exists(join(abspath("."), 'mp4.mp4')):
                notloaded = False
                fname = 'mp4.mp4'

            if exists(join(abspath("."), 'mp4')):
                notloaded = False
                fname = 'mp4'

            sleep(1)

        # Rename video to normal look depending on fname
        move(join(abspath("."), fname), join(abspath("."), str(links[i].text) + ".mp4"))
        print('Загрузка завершена.')
        print('---\n')

    print('\n---\n')
