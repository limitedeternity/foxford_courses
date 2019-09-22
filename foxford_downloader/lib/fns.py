import asyncio
from collections import deque
from datetime import datetime
from pathlib import Path
from re import Match, match
from typing import Dict, Iterable, List, Tuple, Union
from urllib import parse

import requests
from bs4 import BeautifulSoup, Tag
from more_itertools import unique_everseen
from pyppeteer import connect

from .browser import get_browser_connection_url
from .helpers import error_handler, pipe
from .requests_cache import CachedResponse, CachedSession


@error_handler
def get_csrf_token(session: CachedSession) -> str:
    csrf_token_get_response: CachedResponse = session.get(
        "https://foxford.ru/api/csrf_token",
        headers={
            "X-Requested-With": "XMLHttpRequest"
        }
    )

    if csrf_token_get_response.status_code != 200:
        return {"fatal_error": "CSRF token fetch has failed"}

    if "token" not in csrf_token_get_response.json():
        return {"fatal_error": "CSRF token structure is unknown"}

    return csrf_token_get_response.json()["token"]


@error_handler
def login(email: str, password: str, session: CachedSession) -> CachedSession:
    if not email or not password:
        return {"fatal_error": "No credentials provided"}

    credential_post_response: CachedResponse = session.post(
        "https://foxford.ru/user/login",
        headers={
            "X-CSRF-Token": get_csrf_token(session),
            "X-Requested-With": "XMLHttpRequest"
        },
        json={
            "user": {
                "email": email,
                "password": password
            }
        }
    )

    if credential_post_response.status_code != 200:
        return {"fatal_error": "Wrong credentials"}

    return session


def get_user_courses(session: CachedSession) -> Tuple[Dict]:
    @error_handler
    def recursive_collection(page_num: int) -> Tuple[Dict]:
        course_list_response: CachedResponse = session.get(
            f"https://foxford.ru/api/user/bookmarks?page={page_num}&archived=false",
            headers={
                "X-CSRF-Token": get_csrf_token(session),
                "X-Requested-With": "XMLHttpRequest"
            }
        )

        if course_list_response.status_code != 200:
            return {"fatal_error": "Course list fetch has failed"}

        if "bookmarks" not in course_list_response.json():
            return {"fatal_error": "Course list structure is unknown"}

        if all(False for _ in course_list_response.json()["bookmarks"]):
            return ()

        if not {"name", "subtitle", "resource_id"}.issubset(set(course_list_response.json()["bookmarks"][0])):
            return {"fatal_error": "Course structure is unknown"}

        return (
            *course_list_response.json()["bookmarks"],
            *recursive_collection(page_num + 1)
        )

    return recursive_collection(1)


class get_course_lessons():
    @error_handler
    def __new__(self, course_id: int, session: CachedSession) -> Iterable[Dict]:
        lesson_list_at_somewhere_response: CachedResponse = session.get(
            f"https://foxford.ru/api/courses/{course_id}/lessons",
            headers={
                "X-Requested-With": "XMLHttpRequest"
            }
        )

        if lesson_list_at_somewhere_response.status_code != 200:
            return {"fatal_error": "Lesson list fetch has failed"}

        if not {"lessons", "cursors"}.issubset(set(lesson_list_at_somewhere_response.json())):
            return {"fatal_error": "Lesson list structure is unknown"}

        if "id" not in lesson_list_at_somewhere_response.json()["lessons"][0]:
            return {"fatal_error": "Lesson structure is unknown"}

        self.course_id = course_id
        self.session = session

        return pipe(
            lambda json: (
                *self.recursive_collection(
                    self,
                    "before",
                    json["cursors"]["before"]
                ),
                *json["lessons"],
                *self.recursive_collection(
                    self,
                    "after",
                    json["cursors"]["after"]
                )
            ),
            lambda lessons: map(
                lambda lesson: self.lesson_extension(self, lesson),
                lessons
            )
        )(lesson_list_at_somewhere_response.json())

    @error_handler
    def recursive_collection(self, direction: str, cursor: Union[int, None]) -> Tuple[Dict]:
        if not cursor:
            return ()

        lesson_list_at_direction_response: CachedResponse = self.session.get(
            f"https://foxford.ru/api/courses/{self.course_id}/lessons?{direction}={cursor}",
            headers={
                "X-Requested-With": "XMLHttpRequest"
            }
        )

        if lesson_list_at_direction_response.status_code != 200:
            return {"fatal_error": "Lesson list fetch has failed"}

        if not {"lessons", "cursors"}.issubset(set(lesson_list_at_direction_response.json())):
            return {"fatal_error": "Lesson list structure is unknown"}

        if "id" not in lesson_list_at_direction_response.json()["lessons"][0]:
            return {"fatal_error": "Lesson structure is unknown"}

        if direction == "before":
            return (
                *self.recursive_collection(
                    self,
                    direction,
                    lesson_list_at_direction_response
                    .json()["cursors"][direction]
                ),
                *lesson_list_at_direction_response.json()["lessons"]
            )
        else:
            return (
                *lesson_list_at_direction_response.json()["lessons"],
                *self.recursive_collection(
                    self,
                    direction,
                    lesson_list_at_direction_response
                    .json()["cursors"][direction]
                )
            )

    @error_handler
    def lesson_extension(self, lesson: Dict) -> Dict:
        lesson_extension_response: CachedResponse = self.session.get(
            f"https://foxford.ru/api/courses/{self.course_id}/lessons/{lesson['id']}",
            headers={
                "X-Requested-With": "XMLHttpRequest"
            }
        )

        if lesson_extension_response.status_code != 200:
            return {"fatal_error": "Lesson extension fetch has failed"}

        if not {"webinar_id", "access_state", "webinar_status", "is_locked"}.issubset(set(lesson_extension_response.json())):
            return {"fatal_error": "Lesson extension structure is unknown"}

        return lesson_extension_response.json()


class get_resources_for_lessons():
    def __new__(self, course_id: int, webinar_ids: Iterable[int], session: CachedSession) -> Tuple[Dict]:
        self.course_id = course_id
        self.webinar_ids = webinar_ids
        self.session = session
        return self.recursive_collection(self)

    @error_handler
    def recursive_collection(self) -> Tuple[Dict]:
        webinar_id: Union[int, None] = next(self.webinar_ids, None)

        if not webinar_id:
            return ()

        video_source_response: CachedResponse = self.session.get(
            f"https://foxford.ru/groups/{webinar_id}"
        )

        if video_source_response.status_code != 200:
            return {"fatal_error": "Video source fetch has failed"}

        return (
            pipe(
                lambda res: self.retrieve_erly_iframe_src(self, res),
                lambda src: self.construct_resource_links(self, src)
            )(video_source_response),
            *self.recursive_collection(self)
        )

    @error_handler
    def retrieve_erly_iframe_src(self, video_source_response: CachedResponse) -> str:
        erly_iframe: Union[Tag, None] = pipe(
            lambda r_content: BeautifulSoup(
                r_content,
                "html.parser"
            ),
            lambda soup: soup.select_one(
                "div.full_screen > iframe"
            )
        )(video_source_response.content)

        if not erly_iframe:
            return {"fatal_error": ".full_screen > iframe wasn't found"}

        erly_iframe_src: Union[str, None] = erly_iframe.get("src")

        if not erly_iframe_src:
            return {"fatal_error": ".full_screen > iframe doesn't have src attribute"}

        return erly_iframe_src

    @error_handler
    def construct_resource_links(self, erly_iframe_src: str) -> Dict:
        search_params: Dict = dict(
            parse.parse_qsl(
                parse.urlparse(erly_iframe_src).query
            )
        )

        if not {"conf", "access_token"}.issubset(set(search_params)):
            return {"fatal_error": "Iframe src search params structure is unknown"}

        webinar_id_match: Union[Match, None] = match(
            r"^webinar-(\d+)$", search_params.get("conf")
        )

        if not webinar_id_match:
            return {"fatal_error": "Unable to extract webinar id"}

        return {
            "video": f"https://storage.netology-group.services/api/v1/buckets/ms.webinar.foxford.ru/sets/{webinar_id_match[1]}/objects/mp4?access_token={search_params.get('access_token')}",
            "events": f"https://storage.netology-group.services/api/v1/buckets/meta.webinar.foxford.ru/sets/{webinar_id_match[1]}/objects/events.json?access_token={search_params.get('access_token')}"
        }


def get_lesson_tasks(lesson_ids: Iterable[int], session: CachedSession) -> Iterable[List[Dict]]:
    @error_handler
    def fetch(lesson_id: int) -> List[Dict]:
        tasks_response: CachedResponse = session.get(
            f"https://foxford.ru/api/lessons/{lesson_id}/tasks",
            headers={
                "X-Requested-With": "XMLHttpRequest"
            }
        )

        if tasks_response.status_code != 200:
            return {"fatal_error": "Tasks fetch has failed"}

        if "id" not in tasks_response.json()[0]:
            return {"fatal_error": "Task structure is unknown"}

        return tasks_response.json()

    return map(fetch, lesson_ids)


def construct_task_urls(lesson_ids: Iterable[int], lesson_tasks: Iterable[List[Dict]]) -> Iterable[Iterable[str]]:
    def combination(lesson_id: int, task_list: List[Dict]) -> Iterable[str]:
        return map(
            lambda task: f"https://foxford.ru/lessons/{lesson_id}/tasks/{task['id']}",
            task_list
        )

    return map(
        combination,
        lesson_ids,
        lesson_tasks
    )


def construct_conspect_urls(lesson_ids: Iterable[int], conspect_amount: Iterable[int]) -> Iterable[Tuple[str]]:
    def recursive_collection(lesson_id: int, amount: int) -> Tuple[str]:
        if amount == 0:
            return ()

        return (
            *recursive_collection(lesson_id, amount - 1),
            f"https://foxford.ru/lessons/{lesson_id}/conspects/{amount}"
        )

    return map(
        recursive_collection,
        lesson_ids,
        conspect_amount
    )


def build_dir_hierarchy(course_name: str, course_subtitle: str, grade: str, lessons: Iterable[Dict]) -> Iterable[Path]:
    def sanitize_string(string: str) -> str:
        return pipe(
            lambda char_list: filter(
                lambda char: char.isalpha() or char.isdigit() or char == " ", char_list
            ),
            lambda iterable: "".join(iterable),
            lambda filtered_char_list: filtered_char_list[:30].strip()
        )(string)

    def create_dir(lesson: Dict) -> Path:
        constructed_path: Path = Path(
            Path.cwd(),
            (
                f"({grade}) " +
                sanitize_string(course_name) +
                " - " +
                sanitize_string(course_subtitle)
            ).strip(),
            (
                f"({lesson['number']}) " +
                sanitize_string(lesson['title'])
            ).strip()
        )

        if not constructed_path.exists():
            constructed_path.mkdir(parents=True)

        return constructed_path

    return map(
        create_dir,
        lessons
    )


def download_resources(res_with_path: Dict, session: CachedSession) -> None:
    @error_handler
    def download_url(url: str, dest: Path) -> None:
        with requests.get(url, stream=True) as r:
            if r.status_code != 200:
                return {"fatal_error": "Video fetch has failed"}

            with dest.open("wb") as f:
                deque(
                    map(
                        lambda chunk: f.write(chunk),
                        filter(None, r.iter_content(10 * 1024))
                    ),
                    0
                )

    def save_video() -> None:
        if res_with_path["destination"].joinpath("video.mp4").exists():
            return

        download_url(
            res_with_path["video"],
            res_with_path["destination"].joinpath("video.mp4")
        )

    @error_handler
    def parse_and_save_event_data() -> None:
        if res_with_path["destination"].joinpath("message_log.txt").exists():
            return

        events_response: CachedResponse = session.get(
            res_with_path["events"]
        )

        if events_response.status_code != 200:
            return {"fatal_error": "Events fetch has failed"}

        if "meta" not in events_response.json()[0]:
            return {"fatal_error": "Events structure is unknown"}

        with res_with_path["destination"].joinpath("message_log.txt").open("w", errors="replace") as f:
            pipe(
                lambda json: filter(
                    lambda obj: obj["meta"]["action"] == "message",
                    json
                ),
                lambda messages: map(
                    lambda msg: f"[{datetime.fromtimestamp(msg['meta']['time'])}] {msg['meta']['user_name']}: {parse.unquote(msg['meta']['body'])}",
                    messages
                ),
                lambda message_log: "\n".join(message_log),
                f.write
            )(events_response.json())

        pipe(
            lambda json: filter(
                lambda obj:
                    (obj["meta"]["action"] == "add_tab" or
                     obj["meta"]["action"] == "change_tab") and
                    obj["meta"]["content_type"] == "pdf",
                json
            ),
            lambda pdfs: map(
                lambda pdf: pdf["meta"]["url"],
                pdfs
            ),
            unique_everseen,
            lambda urls: enumerate(urls, 1),
            lambda enumed_urls: map(
                lambda item: download_url(
                    item[1],
                    res_with_path["destination"]
                    .joinpath(f"{item[0]}.pdf")
                ),
                enumed_urls
            ),
            lambda task_map: deque(task_map, 0)
        )(events_response.json())

    save_video()
    parse_and_save_event_data()
    print(
        f"-> {res_with_path['destination'].name}: \033[92m\u2713\033[0m"
    )


async def save_page(url: str, path: Path, folder: str, cookies: Iterable[Dict], semaphore: asyncio.Semaphore) -> None:
    async with semaphore:
        if not path.joinpath(folder).joinpath(url.split("/")[-1] + ".pdf").exists():
            browser_endpoint = await get_browser_connection_url()
            browser = await connect(browserWSEndpoint=browser_endpoint)
            page = await browser.newPage()
            await page.emulateMedia("screen")
            await page.setViewport({"width": 411, "height": 823})
            await page.setCookie(*cookies)
            await page.goto(url, {"waitUntil": "domcontentloaded"})

            if await page.waitForFunction("() => window.MathJax", timeout=10000):
                await asyncio.sleep(3.5)
                await page.evaluate("""
                    async function() {
                        await new Promise(function(resolve) {
                            window.MathJax.Hub.Register.StartupHook(
                                "End",
                                resolve
                            )
                        })
                    }
                """)
                await asyncio.sleep(0.1)

            await page.evaluate("""
                document.querySelectorAll(".toggle_element > .toggle_content").forEach(el => el.style.display = "block")
            """, force_expr=True)
            await asyncio.sleep(0.1)

            await page.evaluate("""
                document.querySelector("#cc_container").remove()
            """, force_expr=True)
            await asyncio.sleep(0.1)

            if not path.joinpath(folder).exists():
                path.joinpath(folder).mkdir()

            path.joinpath(folder).joinpath(url.split("/")[-1] + ".pdf").touch()

            await page.pdf({
                "path": str(path.joinpath(folder).joinpath(url.split("/")[-1] + ".pdf")),
                "printBackground": True
            })

            await page.close()
            await browser.disconnect()

        print(
            f"-> {folder}/{url.split('/')[-3]}/{url.split('/')[-1]}: \033[92m\u2713\033[0m"
        )
