from io import open
from htmlfun.elements import body, h3, a, p
from htmlfun import build_doc


def theory_html_gen(course_name, theoretic_data):
    content_links = []

    for name, link in theoretic_data.items():
        content_links += p(a({"href": str(link)}, str(name)))

    doc = build_doc(body(h3(course_name), content_links))

    with open(course_name + "_theory.html", "w", encoding="utf-8") as html_file:
        html_file.write(doc)
