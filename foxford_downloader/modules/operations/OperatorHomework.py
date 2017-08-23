'''Imports'''


from time import sleep

from .SortFiles import sort_files
from .VideoHTML import video_html_gen
from .HomeworkHTML import homework_html_gen
from .Downloader import video_download, homework_download

from selenium.common.exceptions import ElementNotVisibleException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from sys import exit


def operator_homework(driver, course_link):
	lesson_name = None
	course_name = None
	subject_name = None
	main_window = driver.current_window_handle
	homework_links = {}
	download_links = {}

	driver.get(course_link)
	print('\n')

	try:
		course_name = str(driver.find_element_by_class_name("course_info_title").text).replace('"', '').replace("»", "").replace("«", "").replace("!", "").replace("?", "").replace(",", ".").replace("/", "").replace("\\", "").replace(":", "").replace("<", "").replace(">", "").replace("*", "")

		sleep(1)

		subject_name = str(driver.find_element_by_class_name("course_info_subtitle").text).replace('"', '').replace("»", "").replace("«", "").replace("!", "").replace("?", "").replace(",", ".").replace("/", "").replace("\\", "").replace(":", "").replace("<", "").replace(">", "").replace("*", "")

	except ElementNotVisibleException:
		print("Элемент не виден.")
		sleep(1)
		pass

	try:
		driver.find_element_by_class_name("lesson active")
		driver.execute_script("document.getElementsByClassName('lesson active')[0].classList.remove('active');")

	except NoSuchElementException:
		pass

	sleep(0.5)

	lesson_links = driver.find_elements_by_class_name("lesson")
	print('\n---\n')

	for i in range(len(lesson_links) - 1):
						try:
								# Locate and click on it even if not visible
								ActionChains(driver).move_to_element(lesson_links[i]).click(lesson_links[i]).perform()
								sleep(1)

						except ElementNotVisibleException:
								print("Элемент не виден.")
								sleep(1)
								continue

						except StaleElementReferenceException:
								print('Ошибка, связанная с большой задержкой ответа. Попробуй еще раз.')
								sleep(1)
								continue

						try:
								# Set lesson_name...
								lesson_name = str(driver.find_element_by_class_name("lesson_content").find_element_by_tag_name('h2').text).replace('"', '').replace("»", "").replace("«", "").replace("!", "").replace("?", "").replace(",", ".").replace("/", "").replace("\\", "").replace(":", "").replace("<", "").replace(">", "").replace("*", "").replace("_", "")

								print(lesson_name)

						except ElementNotVisibleException:
								print("Элемент не виден.")
								sleep(1)
								continue

						except StaleElementReferenceException:
								print("Название не будет выведено автоматически.")
								continue

						# Video getting
						try:
								# XPATH for video link
								webinar_link = driver.find_element_by_xpath("//i[@class='fxf_icon_small fxf_icon_video_blue']/..")
								if webinar_link is not None and webinar_link.get_attribute("class") != 'disabled':

										# Open link in new tab and switch to it
										driver.execute_script('window.open(arguments[0], "_blank");', webinar_link.get_attribute("href"))

										windows = driver.window_handles
										driver.switch_to.window(windows[1])
										sleep(1)

										# HTML escape characters needed to handle ReactJS case of video extraction
										html_escape_table = {
											"&": "&amp;",
											'"': "&quot;",
											"'": "&apos;",
											">": "&gt;",
											"<": "&lt;",
										}

										# Handling different scenarios - with old player (HTML5) and new (ReactJS-based) player.
										# HTML5 case
										try:
												# Bind lesson name to video link
												download_links[lesson_name] = driver.find_element_by_class_name("vjs-tech").get_attribute("src")
												print("Видео получено.")
												sleep(1)

										except NoSuchElementException:

												# If not HTML5, try ReactJS case.
												try:
														sleep(1)
														video_link = "".join(html_escape_table.get(c, c) for c in driver.find_element_by_class_name("full_screen").find_element_by_tag_name("iframe").get_attribute("src"))
														driver.execute_script('window.open(arguments[0], "_self");', video_link)
														sleep(1)

														# Bind lesson name to video link using dictionary
														download_links[lesson_name] = driver.find_element_by_class_name("vjs-tech").get_attribute("src")
														print("Видео получено.")
														sleep(1)

												except NoSuchElementException:

														# "Shit happened" case
														print('Что-то пошло не так. Закрой все прочие браузеры и после 3-4 повторных попыток сообщи разработчику о проблеме.')
														sleep(1)
														exit(0)

										# Close tab and go for theory
										driver.execute_script('window.close();')
										driver.switch_to.window(main_window)
										sleep(1)

								# For case when video is just disabled (when lesson will take place in future)
								else:
										print('Видео отключено.')
										print('Идем дальше.')
										sleep(1)

								print('---\n')

						# No video (Yeah, that happens too)
						except NoSuchElementException:
								print("Видео не обнаружено.")
								print("Ищу ДЗ.")
								print('---\n')
								sleep(1)

						# HW getting
						try:
								# XPATH for homework link
								homework_link = driver.find_element_by_xpath("//i[@class='fxf_icon_small fxf_icon_tasks_blue']/..")
								if homework_link is not None and homework_link.get_attribute("class") != 'disabled':

										driver.execute_script('window.open(arguments[0], "_blank");', homework_link.get_attribute("href"))

										windows = driver.window_handles
										driver.switch_to.window(windows[1])
										sleep(1)

										# Write to dictionary current url after each click.
										try:
												homework = driver.find_elements_by_xpath("(//div[@class='content-wrapper'])[1]/*[1]/*[position()>1]/*[1]/*[2]")

												for i in range(len(homework)):
														try:
																ActionChains(driver).move_to_element(homework[i]).click(homework[i]).perform()
																sleep(2)
																task_name = driver.find_element_by_xpath("(//div[@class='content-wrapper'])[2]/*[1]/*[1]/*[2]/*[1]").text
																homework_links[lesson_name + "_" + str(task_name).replace('"', '').replace("»", "").replace("«", "").replace("!", "").replace("?", "").replace(",", ".").replace("/", "").replace("\\", "").replace(":", "").replace("<", "").replace(">", "").replace("*", "").replace("_", "")] = driver.current_url
																sleep(1)

														except ElementNotVisibleException:
																print("Элемент не виден.")
																print('---\n')
																sleep(1)

														except StaleElementReferenceException:
																print('Ошибка, связанная с большой задержкой ответа. Попробуй еще раз.')
																print('---\n')
																sleep(1)

														except NoSuchElementException:
																print('Что-то не так.')
																print('---\n')
																sleep(1)

												print("ДЗ записано в очередь.")
												print('---\n')

										except NoSuchElementException:
												print('Произошла ошибка.')
												print('---\n')
												sleep(1)

										# Opening in new tab redirects to dashboard, if HW is not payed
										except IndexError:
												print('Кажется, ДЗ не оплачено.')
												print('---\n')
												sleep(1)

										driver.execute_script('window.close();')
										driver.switch_to.window(main_window)
										sleep(1)

								# HW disabled
								else:
										print('ДЗ отключено.')
										print('Идем дальше.')
										print('---\n')
										sleep(1)

						# No HW
						except NoSuchElementException:
								print("ДЗ не обнаружено.")
								print("Ищу теорию.")
								print('---\n')
								sleep(1)

	# If dictionary with hw is not empty...
	if len(homework_links.keys()) != 0:
			try:
					# Generate HTML from dictionary data
					homework_html_gen(course_name, homework_links)
					print("Список ДЗ сформирован. Скачиваю...")
					print('---\n')

					# Make screenshots
					homework_download(driver, course_name)
					sleep(1)

			except KeyboardInterrupt:
					print("Получение ДЗ сброшено. Продолжаю...")

	# If dictionary with videos is not empty...
	if len(download_links.keys()) != 0:
			# Generate HTML from dictionary data
			video_html_gen(course_name, download_links)
			print("Список видео сформирован. Скачиваю...")
			print('---\n')

			# Start video download
			video_download(driver, course_name, course_link)
			sleep(1)

	sort_files(course_name, subject_name)
	sleep(1)
