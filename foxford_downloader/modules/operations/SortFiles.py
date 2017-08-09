import glob
import os
import shutil


BASE_PATH = os.path.abspath('.')


def sort_videos():
    for filename in glob.glob(os.path.join('*.mp4')):
        os.makedir(filename.strip('.mp4'))
        shutil.move(
            os.path.join(BASE_PATH, filename),
            os.path.join(BASE_PATH, filename.strip('.mp4'), filename)
        )


def sort_materials(file_ext):
    FOLDERS = {'html': 'Теория', 'png': 'ДЗ'}

    for filename in glob.glob(os.path.join('*.%s' % file_ext)):
        folder = os.path.join(filename.split('-')[0], FOLDERS[file_ext])
        if not os.path.isdir(os.path.join(BASE_PATH, folder)):
            os.mkdir(folder)
        shutil.move(
            os.path.join(BASE_PATH, filename),
            os.path.join(
                BASE_PATH, filename.split('-')[0], FOLDERS[file_ext], filename
            )
        )

def sort():
    print('Сортируем видео и материалы по папкам...')
    # sort_videos()
    sort_materials('html')
    sort_materials('png')
    print('Готово.')


sort()