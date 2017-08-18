from io import open as ioopen
from htmlfun.elements import body, h3, a, p
from htmlfun import build_doc


def video_html_gen(course_name, download_links):
	'''HTML generation for corresponding download module'''

	content_links = []

	# Read name and link from dictionary, made by Operator
	for name, link in download_links.items():
		content_links += p(a({"href": str(link), "download": 'mp4.mp4'}, str(name)))

	# Build HTML data
	doc = build_doc(body(h3(course_name), content_links))

	# Write it
	with ioopen(course_name + "_videos.html", "w", encoding="utf-8") as html_file:
		html_file.write(doc)
