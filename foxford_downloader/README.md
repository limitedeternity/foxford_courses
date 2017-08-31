 
 Настройка
====================

Windows
-------

1. Скачай Python 3 для своей платформы (https://www.python.org) и установи, как показано ниже:

![Screenshot1](https://i.imgur.com/24fZCce.png)
![Screenshot2](https://i.imgur.com/BDjiTsJ.png)
![Screenshot3](https://i.imgur.com/fyLH7tD.png)

2. Импортируй `longpath_fixer.reg` на всякий случай.
3. Запусти `pip install selenium Pillow htmlfun`. 

Linux
-----

1. `sudo apt-get update && sudo apt-get install python3.6 python3.6-dev python3.6-venv`

2. `wget https://bootstrap.pypa.io/get-pip.py && sudo python3.6 get-pip.py`

3. `sudo ln -s /usr/bin/python3.6 /usr/local/bin/python3`

4. `sudo ln -s /usr/local/bin/pip /usr/local/bin/pip3`

5. `python3 --version`. Если вывод - 3.6.2, или что-то близкое, то ты победил.

6. `pip3 -V`. Если вывело что-то, значит, все хорошо.

7. `sudo pip3 install --upgrade pip setuptools wheel`

8. `sudo pip3 install selenium Pillow htmlfun`

Mac OSX
-------

1. `xcode-select -p && xcode-select --install`

2. Убедись, что никаких Python не установлено командой:  `ls /Library/Frameworks/Python.framework/Versions/`. Если установлено, то делаешь следующее: `sudo rm -rf /Library/Frameworks/Python.framework && cd /usr/local/bin && ls -l . | grep '../Library/Frameworks/Python.framework' | awk '{print $9}' | xargs sudo rm` И удаляешь из папки Applications все, что хотя бы отдаленно напоминает Python (папки, приложения).

3. `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

4. `brew prune && brew doctor`

5. `brew install python3`

6. `sudo pip3 install --upgrade pip setuptools wheel`

7. `nano ~/.bash_profile`. Стираешь все Backspace'ом, переносясь стрелками, если надо, и вписываешь единственное `export PATH=/usr/local/bin:$PATH`. Жмешь Ctrl + O, затем Enter, затем Ctrl + X.

8. `source ~/.bash_profile`

9. `python3 --version`. Если вывод - 3.6.2, или что-то близкое, то ты победил.

10. `sudo pip3 install selenium Pillow htmlfun`

--------------------

  Работа с утилитой
====================

1. Установи Google Chrome(v58-60). Потом удалишь, если захочешь.

2. Запусти скрипт (`python foxford_dl.py` - на Windows, `python3 foxford_dl.py` - на Mac OSX и Linux). Откроется окно Chrome. Если запустил в первый раз, то залогинься. Разверни окно так, чтобы содержимое сайта помещалось, и перейди на страницу курса.

3. Сходи попей чаю. Ты поймешь, если нужно будет что-то сделать.

!! Полностью тестировался скрипт только на Windows 10. 

!! Максимальное разрешение для работы скриншотов - 1920x1080.

--------------------

Чейнджлог (Крупные апдейты)
====================

---

18.06.2017 (v1)
---

Реализована первая версия методом "проб и ошибок".

С помощью расширения (https://chrome.google.com/webstore/detail/network-sniffer/coblekblkacfilmgdghecpekhadldjfj) необходимо перехватить момент перехода к видео. Нажав на поле со ссылкой, соответствующей видео, откроется поле, где в Request Headers будет параметр Cookie. 

В скрипт вводится 2 значения: адрес видео и куки. На выходе получается файл b64.html, в котором находится ссылка, при переходе по которой происходило перенаправление на плеер, выдающий mp4, который качался с помощью расширения (https://chrome.google.com/webstore/detail/video-downloader-pro/ilppkoakomgpcblpemgbloapenijdcho).

(Отдельное спасибо *Paravozik_Lesha* за тестирование пре-релизной версии и терпение моего характера c: )

---

21.06.2017 (v2)
---

Реализована полу-автоматическая система.

Вбивается ссылка на видео и человека перенаправляет сразу в плеер, где с помощью нажатия "Сохранить как..." можно сохранить вебинар на диск (логично). 

Примерно тогда же была реализована система сохранения ДЗ в оффлайн.

---

30.07.2017 (v3)
---

Реализована полная автоматика и какой-никакой интерфейс.

Все скрипты были объединены в один.

Перевод на русский язык (да-да, наканецта).

Загрузка курсов была переписана *Stanley Kowalski*. Пришлось много чинить, конечно, но это не отменяет моего "спасиба" за факт реализации "другим способом" и то, что именно он подтолкнул меня на объединение обоих скриптов.

---

05.08.2017 (v4)
---

Исправлено множество ошибок.

Разделение на модули для легкости починки.

Добавлено сохранение теории и ДЗ.

Объединение всех действий в единый оператор. За один проход теперь можно скачать весь материал полностью.

Сделан режим "только видео" и сортировка материала. (Отдельное спасибо *@kuzminovdmit*)

Добавлено возобновление загрузки на случай, если что-то пойдет не так, чтобы не ждать по-новой. Необходимо просто выбрать после перезапуска пункт меню, который выбирался до этого.

Создание файла "video.skips", содержащего число, приведет к пропуску видео на соответствующее число. (0 - Вводное занятие, 1 - Первое + Вводное ...)

--------

*Current version*: v4.1-rstable1

--------

Original idea + Releases: limitedeternity

Testing + Ideas: Stanley Kowalski / Paravozik_Lesha

VideoDownloader(): Stanley Kowalski (v3)

(Специально для 2ch.hk/un/)
