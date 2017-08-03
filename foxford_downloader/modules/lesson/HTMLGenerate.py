from io import open
from htmlfun.elements import body, h3, a, p
from htmlfun import build_doc


def generate_html_file(course_name, download_links):
    content_links = []

    for name, link in download_links.items():
        content_links += p(a({"href": str(link), "download": str(name) + ".mp4"}, str(name)))

    doc = build_doc(body(h3(course_name), content_links))

    with open("links.html", "w", encoding="utf-8") as html_file:
        html_file.write(doc)
