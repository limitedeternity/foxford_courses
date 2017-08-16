from os import unlink, listdir
from io import open as ioopen
from os.path import join, abspath
from shutil import move


def sort_files(course_name):
    for filename in listdir(abspath(".")):
        if filename.endswith(".mp4"):
            move(
                join(abspath('.'), filename),
                join(abspath('.'), course_name, filename.strip('.mp4'), filename)
            )

        elif filename.endswith(".png"):
            move(
                join(abspath('.'), filename),
                join(abspath('.'), course_name, "Теория", filename)
            )

        elif filename.endswith(".html"):
            unlink(join(abspath('.'), filename))

    with ioopen(join(abspath('.'), 'links.txt'), "w") as ph:
        ph.write("<-- PLACEHOLDER [REPLACE ME] -->")
