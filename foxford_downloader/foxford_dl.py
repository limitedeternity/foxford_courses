# -*- coding: utf-8 -*-

from os import chdir, remove, urandom, system
from os.path import dirname, abspath, isfile
from sys import platform, exit
from platform import machine
from time import sleep
from re import match
from io import open as ioopen
from subprocess import call
from PIL import Image
from binascii import hexlify

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException, StaleElementReferenceException

from htmlfun.elements import body, h3, a, p
from htmlfun import build_doc


def cls():
    if platform.startswith('win'):
        system('cls')

    else:
        system('clear')


def shutdown_chrome():
    if platform.startswith('win'):
            call('taskkill /F /IM chrome.exe', shell=True)

    elif platform.startswith('darwin'):
            call('pkill -a -i "Google Chrome"', shell=True)

    elif platform.startswith('linux'):
            call('kill -9 `ps -A |grep chrome| cut -d "?" -f1`', shell=True)

    else:
        print("Поставь нормальную систему.")
        sleep(1)
        cls()
        exit(0)


def selector():
    shutdown_chrome()
    print("\n------------------------------")
    print("1. Сделать скриншот ДЗ")
    print("2. Скачать курс")
    print("0. Выйти")
    print("------------------------------\n")

    mode = input("Выбирай: ")
    sleep(0.5)

    if mode == '1':
        HomeworkDownloader().run()

    elif mode == '2':
        VideoDownloader().run()

    else:
        cls()
        sleep(1)
        exit(0)


class HomeworkDownloader:

    def __init__(self):
        self.driver_location = self.system_platform()
        self.option = Options()
        self.option.add_argument("user-data-dir=Chrome")
        self.driver = webdriver.Chrome(executable_path=self.driver_location, chrome_options=self.option)

    def system_platform(self):
        if platform.startswith('win'):
            return 'driver/win/chromedriver.exe'
        elif platform.startswith('darwin'):
            return 'driver/darwin/chromedriver'
        elif platform.startswith('linux'):
            if machine().endswith('64'):
                return 'driver/linux/x64/chromedriver'
            else:
                return 'driver/linux/x86/chromedriver'
        else:
            print("Поставь нормальную систему.")
            sleep(1)
            cls()
            exit(0)

    def login_to_foxford(self):
        self.driver.get("https://foxford.ru/user/login/")

    def run(self):
        self.login_to_foxford()

        while True:
            try:
                homework_link = input("Вставь ссылку на ДЗ сюда: ")
                self.make_screenshot(homework_link)

            except KeyboardInterrupt:
                cls()
                selector()

    def fullpage_screenshot(self, file):
        total_width = self.driver.execute_script("return document.body.offsetWidth;")
        total_height = self.driver.execute_script("return document.body.parentNode.scrollHeight;")
        viewport_width = self.driver.execute_script("return document.body.clientWidth;")
        viewport_height = self.driver.execute_script("return window.innerHeight;")
        rectangles = []

        i = 0
        while i < total_height:
            ii = 0
            top_height = i + viewport_height

            if top_height > total_height:
                top_height = total_height

            while ii < total_width:
                top_width = ii + viewport_width

                if top_width > total_width:
                    top_width = total_width

                rectangles.append((ii, i, top_width, top_height))

                ii += viewport_width

            i += viewport_height

        stitched_image = Image.new('RGB', (total_width, total_height))
        previous = None
        part = 0

        for rectangle in rectangles:
            if previous is not None:
                self.driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
                sleep(0.2)

            file_name = "part_{0}.png".format(part)

            self.driver.get_screenshot_as_file(file_name)
            screenshot = Image.open(file_name)

            if rectangle[1] + viewport_height > total_height:
                offset = (rectangle[0], total_height - viewport_height)
            else:
                offset = (rectangle[0], rectangle[1])

            stitched_image.paste(screenshot, offset)

            del screenshot
            remove(file_name)
            part += 1
            previous = rectangle

        stitched_image.save(file)
        return True

    def make_screenshot(self, homework_link):
        self.driver.get(homework_link)
        self.driver.execute_script("document.getElementById('headerComponent').setAttribute('style', 'display:none;');")

        height = self.driver.execute_script("return window.screen.height;")
        width = self.driver.execute_script("return window.screen.width;")
        self.driver.set_window_size(width, height)

        rand = str(hexlify(urandom(3))).strip('b').replace("'", "")

        self.fullpage_screenshot("homework_" + rand + ".png")
        print("Скриншот сохранен, как " + "'homework_" + rand + ".png'." + " Чтобы выйти, нажми Ctrl + C.\n")


class VideoDownloader:

    def __init__(self):
        self.driver_location = self.system_platform()
        self.option = Options()
        self.option.add_argument("user-data-dir=Chrome")
        self.option.add_extension('./download_manager.crx')
        self.driver = webdriver.Chrome(executable_path=self.driver_location, chrome_options=self.option)
        self.main_window = self.driver.current_window_handle
        self.course_name = ''
        self.download_links = {}

    def system_platform(self):
        if platform.startswith('win'):
            return 'driver/win/chromedriver.exe'
        elif platform.startswith('darwin'):
            return 'driver/darwin/chromedriver'
        elif platform.startswith('linux'):
            if machine().endswith('64'):
                return 'driver/linux/x64/chromedriver'
            else:
                return 'driver/linux/x86/chromedriver'
        else:
            print("Поставь нормальную систему.")
            sleep(1)
            cls()
            exit(0)

    def login_to_foxford(self):
        self.driver.get("about:blank")
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.get("https://foxford.ru/user/login/")
        height = self.driver.execute_script("return window.screen.height;")
        width = self.driver.execute_script("return window.screen.width;")
        self.driver.set_window_size(width, height)

    def run(self):
        self.login_to_foxford()

        while True:
            try:
                course_link = input("Вставь ссылку на курс сюда: ")

                if isfile('./links.html'):
                    remove('./links.html')

                else:
                    pass

                if match(r"^((https?):\/\/)(foxford\.ru\/)(courses\/)(\d{3})(\/?)$", course_link):
                    self.collect_lesson_links(course_link)
                else:
                    print('Ссылка должна быть такой: https://foxford.ru/courses/xxx, где xxx - 3 цифры курса.')

            except KeyboardInterrupt:
                if isfile('./links.html'):
                    remove('./links.html')

                else:
                    pass

                cls()
                selector()

    def collect_lesson_links(self, course_link):
        self.driver.get(course_link)
        self.course_name = self.driver.find_element_by_class_name("course_info_title").text
        print(self.course_name)
        lesson_links = self.driver.find_elements_by_class_name("lesson")
        sleep(0.5)
        self.crawling_links(lesson_links)

    def crawling_links(self, lesson_links):
        for lesson_link in lesson_links:
            try:
                lesson_link.click()
                sleep(1)

            except ElementNotVisibleException:
                continue

            try:
                lesson_name = self.driver.find_element_by_class_name("lesson_content").find_element_by_tag_name('h2').text
                print(lesson_name)

            except StaleElementReferenceException:
                continue

            try:
                webinar_link = self.driver.find_element_by_class_name("webinar_status_box").find_element_by_tag_name("a")
                if webinar_link is not None and webinar_link.get_attribute("class") != 'disabled':

                    self.driver.execute_script('window.open("{}","_blank");'.format(webinar_link.get_attribute("href")))

                    windows = self.driver.window_handles
                    self.driver.switch_to.window(windows[1])

                    html_escape_table = {
                        "&": "&amp;",
                        '"': "&quot;",
                        "'": "&apos;",
                        ">": "&gt;",
                        "<": "&lt;",
                    }

                    video_link = "".join(html_escape_table.get(c, c) for c in self.driver.find_element_by_class_name("full_screen").find_element_by_tag_name("iframe").get_attribute("src"))
                    self.driver.execute_script('window.open("{}","_self");'.format(video_link))

                    self.download_links[lesson_name] = self.driver.find_element_by_class_name("vjs-tech").get_attribute("src")
                    print("Видео получено.")

                    self.driver.execute_script('window.close();')
                    self.driver.switch_to.window(self.main_window)
                    sleep(1)

                else:
                    print('Видео не существует.')

                print('---\n')

            except NoSuchElementException:
                print("Ссылки нет. Идем дальше...")
                continue

        self.generate_html_file(self.course_name, self.download_links)

    def generate_html_file(self, course_name, download_links):
        content_links = []

        for k, v in download_links.items():
            content_links += p(a({"href": "{}".format(v), "download": "{}.mp4".format(k)}, "{}".format(k)))

        doc = build_doc(body(h3(course_name), content_links))

        with ioopen("links.html", "w", encoding="utf-8") as html_file:
            html_file.write(doc)

        self.download()
        print('Готово. Если хочешь выйти, нажми Ctrl + C.\n')

    def download(self):
        self.driver.get('file://' + abspath('links.html'))
        links = self.driver.find_elements_by_tag_name("a")

        for link in links:
            try:
                link.click()

            except ElementNotVisibleException:
                continue

            sleep(1.5)


if __name__ == "__main__":
    chdir(dirname(abspath(__file__)))
    selector()
