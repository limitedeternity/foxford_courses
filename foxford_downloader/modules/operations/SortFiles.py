import glob
import os
import shutil


def sort_files(course_name):
    for filename in glob.glob(os.path.join(os.path.abspath('.'), '*.mp4')):
        os.makedirs(filename.strip('.mp4'))
        shutil.move(
            os.path.join(os.path.abspath('.'), filename),
            os.path.join(os.path.abspath('.'), course_name, filename.strip('.mp4'), filename)
        )

    for filename in glob.glob(os.path.join(os.path.abspath('.'), '*.png')):
        if not os.path.isdir("Теория"):
            os.makedirs("Теория")

        shutil.move(
            os.path.join(os.path.abspath('.'), filename),
            os.path.join(os.path.abspath('.'), course_name, "Теория", filename)
        )
