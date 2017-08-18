import os
import requests
from bs4 import BeautifulSoup


def reciever():
	MAX_RETRIES = 20

	url = input("Webinar url: ")
	cookie = input("Cookie: ")

	headers = {'Full URL': url, 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8', 'DNT': '1', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,ja;q=0.2,fr;q=0.2', 'Cookie': cookie}
	session = requests.Session()
	adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
	session.mount('https://', adapter)
	session.mount('http://', adapter)

	data = session.get(url, headers=headers)
	with open('b64.html', 'wb') as output:
		output.write(data.content)
	parser()


def parser():
	with open('b64.html', 'r') as html_doc:
		data = html_doc.read()

	soup = BeautifulSoup(data, "lxml")
	link = soup.find_all('iframe')
	link = str(link)
	with open('b64.html', 'w') as link_write:
		link_write.write(link)

if __name__ == "__main__":
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	reciever()
