from io import open
from htmlfun.elements import body, h3, a, p
from htmlfun import build_doc


def homework_html_gen(course_name, homework_links):
    content_links = []

    for name, link in homework_links.items():
        content_links += p(a({"href": str(link)}, str(name)))

    doc = build_doc(body(h3(course_name), content_links))

    with open(course_name + "_homework.html", "w", encoding="utf-8") as html_file:
        html_file.write(doc)
