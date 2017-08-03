from time import sleep
from . import element_screenshot
from selenium.common.exceptions import ElementNotVisibleException, StaleElementReferenceException


def homework_operator(driver, homework_link):
    driver.get(homework_link)
    nodes = driver.find_elements_by_class_name("content-wrapper")[0].find_elements_by_css_selector("*")[0].find_elements_by_css_selector("*")
    sleep(1)

    for i in range(len(nodes) - 1):
        try:
            nodes[i].click()
            sleep(1)
            element_screenshot(driver)
            sleep(1)

        except ElementNotVisibleException:
            print("Элемент не виден.")
            sleep(1)
            continue

        except StaleElementReferenceException:
            print('Ошибка, связанная с большой задержкой ответа. Попробуй еще раз.')
            sleep(1)
            continue
