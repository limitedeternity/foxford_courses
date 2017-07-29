# -*- coding: utf-8 -*-

import os
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
import subprocess
import platform


def startup():
	try:
		if sys.platform.startswith('win'):
			subprocess.call('taskkill /F /IM chrome.exe', shell=True)

		elif sys.platform.startswith('darwin'):
			subprocess.call('pkill -a -i "Google Chrome"', shell=True)

		elif sys.platform.startswith('linux'):
			subprocess.call('kill -9 `ps -A |grep chrome| cut -d "?" -f1`', shell=True)

		else:
			print("Unknown system.")
			sys.exit(0)

		opts = Options()
		opts.add_argument("user-data-dir=Chrome")

		if sys.platform.startswith('win'):
			driver = webdriver.Chrome(executable_path="driver/win/chromedriver.exe", chrome_options=opts)

		elif sys.platform.startswith('darwin'):
			driver = webdriver.Chrome(executable_path="driver/darwin/chromedriver", chrome_options=opts)

		elif sys.platform.startswith('linux'):
			if platform.machine().endswith('64'):
				driver = webdriver.Chrome(executable_path="driver/linux/x64/chromedriver", chrome_options=opts)

			else:
				driver = webdriver.Chrome(executable_path="driver/linux/x86/chromedriver", chrome_options=opts)

		else:
			print("Unknown system.")
			sys.exit(0)

		driver.get('https://foxford.ru/user/registration/')
		driver.execute_script("return window.open('https://vk.com');")

		input("Login to foxford (or get webinar URLs). When you are done, press Ctrl + C to continue.")

	except KeyboardInterrupt:
		main()


def main():
	while True:
			try:
				if sys.platform.startswith('win'):
					subprocess.call('taskkill /F /IM chrome.exe', shell=True)

				elif sys.platform.startswith('darwin'):
					subprocess.call('pkill -a -i "Google Chrome"', shell=True)

				elif sys.platform.startswith('linux'):
					subprocess.call('kill -9 `ps -A |grep chrome| cut -d "?" -f1`', shell=True)

				else:
					print("Unknown system.")
					sys.exit(0)

				url = str(input("\nWebinar url: "))
				opts = Options()
				opts.add_argument("user-data-dir=Chrome")

				if sys.platform.startswith('win'):
					driver = webdriver.Chrome(executable_path="driver/win/chromedriver.exe", chrome_options=opts)

				elif sys.platform.startswith('darwin'):
					driver = webdriver.Chrome(executable_path="driver/darwin/chromedriver", chrome_options=opts)

				elif sys.platform.startswith('linux'):
					if platform.machine().endswith('64'):
						driver = webdriver.Chrome(executable_path="driver/linux/x64/chromedriver", chrome_options=opts)

					else:
						driver = webdriver.Chrome(executable_path="driver/linux/x86/chromedriver", chrome_options=opts)

				else:
					print("Unknown system.")
					sys.exit(0)

				driver.get(url)

				data = driver.execute_script("return document.documentElement.innerHTML;")

				soup = BeautifulSoup(data, "lxml")
				iframe = soup.find_all('iframe')[0]
				link = iframe.attrs['src']

				html_escape_table = {
					"&": "&amp;",
					'"': "&quot;",
					"'": "&apos;",
					">": "&gt;",
					"<": "&lt;",
				}

				link = "".join(html_escape_table.get(c, c) for c in link)

				driver.get(link)

				video_location = driver.execute_script("return document.documentElement.innerHTML;")

				soup = BeautifulSoup(video_location, "lxml")
				video = soup.find('video', 'vjs-tech')
				video = video.attrs['src']
				video = "".join(html_escape_table.get(c, c) for c in video)

				driver.get(video)
				actionchains = ActionChains(driver)
				actionchains.context_click().perform()

				print("Waiting for you to download video... Press Enter, when finished.")
				input("Or if you want to exit, press Ctrl + C.")

			except KeyboardInterrupt:
				print('\n')
				sys.exit(0)


if __name__ == "__main__":
	os.chdir(os.path.dirname(os.path.abspath(__file__)))

	startup()
