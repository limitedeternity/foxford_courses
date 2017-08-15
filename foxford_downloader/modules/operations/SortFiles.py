from glob import glob
from os import makedirs, unlink
from os.path import join, abspath
from shutil import move


def sort_files(course_name):
    for filename in glob(join(abspath('.'), '*.mp4')):
        makedirs(filename.strip('.mp4'))
        move(
            join(abspath('.'), filename),
            join(abspath('.'), course_name, filename.strip('.mp4'), filename)
        )

    for filename in glob(join(abspath('.'), '*.png')):
        move(
            join(abspath('.'), filename),
            join(abspath('.'), course_name, "Теория", filename)
        )

    for filename in glob(join(abspath('.'), '*.html')):
        unlink(join(abspath('.'), filename))

    unlink(join(abspath('.'), 'links.txt'))
