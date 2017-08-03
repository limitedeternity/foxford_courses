from os import urandom
from binascii import hexlify
from PIL import Image
from io import BytesIO


def element_screenshot(driver):
    rand = str(hexlify(urandom(3))).strip('b').replace("'", "")
    file = "homework_" + rand + ".png"
    scrollheight = driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")

    slices = []
    offset = 0

    while offset < scrollheight:

        driver.execute_script("window.scrollTo(0, %s);" % offset)

        img = Image.open(BytesIO(driver.get_screenshot_as_png()))

        offset += img.size[1]

        slices.append(img)

    screenshot = Image.new('RGB', (slices[0].size[0], scrollheight))
    offset = 0
    for img in slices:
        screenshot.paste(img, (0, offset))
        offset += img.size[1]

    screenshot.save(file)

    element = driver.find_elements_by_class_name("content-wrapper")[1]
    location = element.location
    size = element.size

    im = Image.open(file)

    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']

    im = im.crop((left, top, right, bottom))
    im.save(file)

    print("Скриншот сохранен, как " + "'homework_" + rand + ".png'.")
    print("---\n")
