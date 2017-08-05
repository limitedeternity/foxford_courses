from os import system
from sys import platform


def cls():
	'''Visual workaround'''

	if platform.startswith('win'):
		system('cls')
	else:
		system('clear')
