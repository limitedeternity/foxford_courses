# pylint: disable = too-many-function-args

from collections import deque
from datetime import datetime
from functools import reduce
from pathlib import Path
from re import Match, match
from typing import Any, Callable, Dict, Iterable, Tuple, Union
from urllib import parse

import requests
from bs4 import BeautifulSoup, Tag
from more_itertools import unique_everseen
from PyInquirer import prompt

from requests_cache import CachedResponse, CachedSession


class Logger():
    @staticmethod
    def error(message: str) -> None:
        print(f"[\033[91mE\033[0m]: \033[1m{message}\033[0m")

    @staticmethod
    def warn(message: str) -> None:
        print(f"[\033[93mW\033[0m]: \033[1m{message}\033[0m")

    @staticmethod
    def log(message: str) -> None:
        print(f"[\033[94mL\033[0m]: \033[1m{message}\033[0m")


def Maybe(t: type) -> Union[Any, None]:
    return Union[t, None]


def pipe(*args: Tuple[Callable]) -> Callable:
    return lambda val: reduce(lambda prev, fn: fn(prev), args, val)


def print_error_and_exit(error_text: str) -> None:
    Logger.error(error_text)
    exit(1)


def error_handler(fn: Callable) -> Callable:
    def wrapper(*args: Tuple, **kwargs: Dict):
        try:
            result: Any = fn(*args, **kwargs)
            if isinstance(result, dict) and "fatal_error" in result:
                print_error_and_exit(result["fatal_error"])

            return result
        except Exception as e:
            print_error_and_exit(e)

    return wrapper


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
        course_list_response: CachedResponse = session.post(
            "https://foxford.ru/api/user/bookmarks/search",
            headers={
                "X-CSRF-Token": get_csrf_token(session),
                "X-Requested-With": "XMLHttpRequest"
            },
            json={
                "page": page_num,
                "discipline_ids": [],
                "resource_types": [],
                "archived": False
            }
        )

        if course_list_response.status_code != 200:
            return {"fatal_error": "Course list fetch has failed"}

        if "bookmarks" not in course_list_response.json():
            return {"fatal_error": "Course list structure is unknown"}

        if all(False for _ in course_list_response.json()["bookmarks"]):
            return {}

        if not {"name", "subtitle", "resource_id"}.issubset(set(course_list_response.json()["bookmarks"][0])):
            return {"fatal_error": "Course structure is unknown"}

        return (
            *course_list_response.json()["bookmarks"],
            *recursive_collection(page_num + 1)
        )

    return recursive_collection(1)


class get_course_lessons():
    @error_handler
    def __new__(self, course_id: int, session: CachedSession) -> Tuple[Dict]:
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
            ),
            tuple
        )(lesson_list_at_somewhere_response.json())

    @error_handler
    def recursive_collection(self, direction: str, cursor: Maybe(int)) -> Tuple[Dict]:
        if not cursor:
            return {}

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
        webinar_id: Maybe(int) = next(self.webinar_ids, None)

        if not webinar_id:
            return {}

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
        erly_iframe: Maybe(Tag) = pipe(
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

        erly_iframe_src: Maybe(str) = erly_iframe.get("src")

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

        webinar_id_match: Maybe(Match) = match(
            r"^webinar-(\d{5})$", search_params.get("conf")
        )

        if not webinar_id_match:
            return {"fatal_error": "Unable to extract webinar id"}

        return {
            "video": f"https://storage.netology-group.services/api/v1/buckets/ms.webinar.foxford.ru/sets/{webinar_id_match[1]}/objects/mp4?access_token={search_params.get('access_token')}",
            "events": f"https://storage.netology-group.services/api/v1/buckets/meta.webinar.foxford.ru/sets/{webinar_id_match[1]}/objects/events.json?access_token={search_params.get('access_token')}"
        }


def build_dir_hierarchy(course_name: str, course_subtitle: str, lesson_titles: Iterable[str]) -> Tuple[Path]:
    def sanitize_string(string: str) -> str:
        return pipe(
            lambda char_list: filter(
                lambda char: char.isalpha() or char.isdigit() or char == " ", char_list
            ),
            lambda iterable: "".join(iterable),
            lambda filtered_char_list: filtered_char_list.strip()[:30]
        )(string)

    def create_path(idx: int, lesson_title: str) -> Path:
        constructed_path: Path = Path(
            Path.cwd(),
            sanitize_string(course_name) + " - " +
            sanitize_string(course_subtitle),
            f"({idx}) " + sanitize_string(lesson_title)
        )

        if not constructed_path.exists():
            constructed_path.mkdir(parents=True, exist_ok=True)

        return constructed_path

    return pipe(
        lambda titles: enumerate(titles, 1),
        lambda enumed_titles: map(
            lambda item: create_path(*item),
            enumed_titles
        ),
        tuple
    )(lesson_titles)


def download_resources(res_with_paths: Iterable[Dict], session: CachedSession) -> None:
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

    def save_video(current_iter_object: Dict) -> None:
        if current_iter_object["destination"].joinpath("video.mp4").exists():
            return

        download_url(
            current_iter_object["video"],
            current_iter_object["destination"].joinpath("video.mp4")
        )

    @error_handler
    def parse_and_save_event_data(current_iter_object: Dict) -> None:
        if current_iter_object["destination"].joinpath("message_log.txt").exists():
            return

        events_response: CachedResponse = session.get(
            current_iter_object["events"]
        )

        if events_response.status_code != 200:
            return {"fatal_error": "Events fetch has failed"}

        with current_iter_object["destination"].joinpath("message_log.txt").open("w") as f:
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
                    current_iter_object["destination"].joinpath(
                        f"{item[0]}.pdf"
                    )
                ),
                enumed_urls
            ),
            lambda task_map: deque(task_map, 0)
        )(events_response.json())

    def recursive_iteration() -> None:
        current_iter_object: Maybe(Dict) = next(res_with_paths, None)

        if not current_iter_object:
            return

        save_video(current_iter_object)
        parse_and_save_event_data(current_iter_object)

        print(
            f"-> {current_iter_object['destination'].name}: \033[92m\u2713\033[0m"
        )

        recursive_iteration()

    recursive_iteration()


def main() -> None:
    session: CachedSession = CachedSession()
    credential_query: Dict = prompt([
        {
            "type": "input",
            "name": "email",
            "message": "Email"
        },
        {
            "type": "password",
            "name": "password",
            "message": "Password"
        }
    ])

    Logger.log("Fetching course list...")

    user_courses: Tuple[Dict] = get_user_courses(
        login(
            credential_query["email"],
            credential_query["password"],
            session
        )
    )

    course_query: Dict = prompt([
        {
            "type": "list",
            "name": "course",
            "message": "Select course",
            "choices": map(lambda obj: f"{obj['name']} - {obj['subtitle']}", user_courses)
        }
    ])

    selected_course: Dict = next(
        filter(
            lambda obj: f"{obj['name']} - {obj['subtitle']}" == course_query["course"],
            user_courses
        )
    )

    Logger.log("Constructing lesson list...")

    available_course_lessons: Tuple[Dict] = pipe(
        lambda cid: get_course_lessons(
            cid,
            session
        ),
        lambda l: filter(
            lambda lesson:
                lesson["access_state"] == "available" and not
                lesson["is_locked"] and
                lesson["webinar_status"] == "video_available",
            l
        ),
        tuple
    )(selected_course["resource_id"])

    Logger.log("Fetching resource links...")

    resources_for_lessons: Tuple[Dict] = get_resources_for_lessons(
        selected_course["resource_id"],
        map(
            lambda obj: obj["webinar_id"],
            available_course_lessons
        ),
        session
    )

    Logger.log("Creating paths...")

    paths: Tuple[Path] = build_dir_hierarchy(
        selected_course["name"],
        selected_course["subtitle"],
        map(
            lambda obj: obj["title"],
            available_course_lessons
        )
    )

    Logger.log("Downloading resources...")

    download_resources(
        map(
            lambda res_obj, path: {
                **res_obj,
                "destination": path
            },
            resources_for_lessons,
            paths
        ),
        session
    )

    Logger.log("Done!")


if __name__ == "__main__":
    main()
