from glob import glob
from os import unlink
from io import open as ioopen
from os.path import join, abspath
from shutil import move


def sort_files(course_name):
    for filename in glob(join(abspath('.'), '*.mp4')):
        if filename is not None:
            move(
                join(abspath('.'), filename),
                join(abspath('.'), course_name, filename.strip('.mp4'), filename)
            )

    for filename in glob(join(abspath('.'), '*.png')):
        if filename is not None:
            move(
                join(abspath('.'), filename),
                join(abspath('.'), course_name, "Теория", filename)
            )

    for filename in glob(join(abspath('.'), '*.html')):
        if filename is not None:
            unlink(join(abspath('.'), filename))

    with ioopen(join(abspath('.'), 'links.txt'), "w") as ph:
        ph.write("<-- PLACEHOLDER [REPLACE ME] -->")
