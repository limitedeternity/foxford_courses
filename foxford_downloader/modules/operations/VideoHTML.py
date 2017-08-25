from io import open as ioopen
from os.path import exists, abspath, join
from os import unlink
from htmlfun.elements import body, h3, a, p
from htmlfun import build_doc


def video_html_gen(course_name, download_links):
	'''HTML generation for corresponding download module'''

	skips = None
	content_links = []

	# Read name and link from dictionary, made by Operator
	for name, link in download_links.items():
		content_links += p(a({"href": str(link), "download": ''}, str(name)))

	if exists(join(abspath("."), 'video.skips')):
		with ioopen('video.skips', 'r', encoding='utf-8') as video_skips:
			skips = int(video_skips.read())

		content_links = content_links[skips + 1:]
		unlink(join(abspath("."), 'video.skips'))

	# Build HTML data
	doc = build_doc(body(h3(course_name), content_links))

	# Write it
	with ioopen(course_name + "_videos.html", "w", encoding="utf-8") as html_file:
		html_file.write(doc)
