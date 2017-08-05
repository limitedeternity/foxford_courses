def login_to_foxford(driver):
	'''Foxford login'''

	driver.get("about:blank")
	driver.switch_to.window(driver.window_handles[0])
	driver.get("https://foxford.ru/user/login/")
