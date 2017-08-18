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
                join(abspath('.'), course_name, filename[:-4], filename)
            )

        # If file is screenshot
        elif filename.endswith(".png"):
            # move it to theory directory
            move(
                join(abspath('.'), filename),
                join(abspath('.'), course_name, "Теория", filename)
            )

        # HTML cleanup for next session
        elif filename.endswith(".html"):
            unlink(join(abspath('.'), filename))
