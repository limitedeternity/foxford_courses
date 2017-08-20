from os import unlink, listdir
from os.path import join, abspath
from shutil import move


def sort_files(course_name):
    '''Sorting for materials'''

    # listing all files
    for filename in listdir(abspath(".")):

        # check if file is video
        if filename.endswith(".mp4"):
            # move it to corresponding directory
            move(
                join(abspath('.'), filename),
                join(abspath('.'), course_name, filename[:-4], "Видео.mp4")
            )

        # we move homework after all, because we are sorting theory before calling sort_files() to avoid conflicts
        elif filename.endswith(".png"):
            # move it to hw directory
            move(
                join(abspath('.'), filename),
                join(abspath('.'), course_name, filename.split('_')[0], "ДЗ-" + filename.split('_')[2])
            )

        # HTML cleanup for next session
        elif filename.endswith(".html"):
            unlink(join(abspath('.'), filename))
