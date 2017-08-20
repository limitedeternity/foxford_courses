from PIL import Image
from time import sleep
from os import unlink


def theory_screenshot(driver, file):

    '''Screenshot module for theory'''

    # Get page parameters
    total_width = driver.execute_script("return document.body.offsetWidth;")
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight;")
    viewport_width = driver.execute_script("return document.body.clientWidth;")
    viewport_height = driver.execute_script("return window.innerHeight;")
    rectangles = []

    # Screenshot module. Handles scrolling and making a fullpage screenshot.
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
            driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
            sleep(0.2)

        file_name = "part_{0}.png".format(part)

        driver.get_screenshot_as_file(file_name)
        screenshot = Image.open(file_name)

        if rectangle[1] + viewport_height > total_height:
            offset = (rectangle[0], total_height - viewport_height)
        else:
            offset = (rectangle[0], rectangle[1])

        # Adding visible block to existing
        stitched_image.paste(screenshot, offset)

        del screenshot
        unlink(file_name)
        part += 1
        previous = rectangle

    # Saving glued image
    stitched_image.save(file)

    # element is a block, containing theory, in page DOM. So, we are getting its parameters.
    element = driver.find_element_by_class_name("page_content")
    location = element.location
    size = element.size

    im = Image.open(file)

    # Preparing a crop mask to cut off unnecessary contents
    left = location['x']
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']

    # Applying crop
    im = im.crop((left, top, right, bottom))

    # Saving result
    im.save(file)

    print("Скриншот сохранен, как " + "'" + file + "'.")
    print("---\n")
