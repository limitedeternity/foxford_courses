from os import system
from sys import platform


def cls():
	'''Cross-platform clean screen'''

	if platform.startswith('win'):
		system('cls')  # <--- "cls" on Windows
	else:
		system('clear')  # <--- "clear" on Unix
