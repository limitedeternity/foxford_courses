from io import open as ioopen
from htmlfun.elements import body, h3, a, p
from htmlfun import build_doc


def homework_html_gen(course_name, homework_links):
    '''HTML generation for corresponding download module'''

    content_links = []

    # Read name and link from dictionary, made by Operator
    for name, link in homework_links.items():
        content_links += p(a({"href": str(link), "target": '_blank'}, str(name)))

    # Build HTML data
    doc = build_doc(body(h3(course_name), content_links))

    # Write it
    with ioopen(course_name + "_homework.html", "w", encoding="utf-8") as html_file:
        html_file.write(doc)
