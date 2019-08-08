import asyncio
from argparse import ArgumentParser, Namespace
from itertools import chain
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from PyInquirer import prompt

from lib.browser import terminate_browser_instance
from lib.fns import *
from lib.helpers import Logger, pipe
from lib.requests_cache import CachedSession


def main(params: Dict) -> None:
    session: CachedSession = CachedSession()
    credential_query: Dict[str, str] = params if params["email"] and params["password"] else prompt([
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

    course_query: Dict[str, str] = prompt([
        {
            "type": "list",
            "name": "course",
            "message": "Select course",
            "choices": map(lambda obj: f"({obj['grades_range']}) {obj['name']} - {obj['subtitle']}", user_courses)
        }
    ])

    selected_course: Dict = next(
        filter(
            lambda obj: f"({obj['grades_range']}) {obj['name']} - {obj['subtitle']}" == course_query["course"],
            user_courses
        )
    )

    Logger.log("Fetching lesson list...")

    (
        course_lessons_with_video,
        course_lessons_with_homework,
        course_lessons_with_conspect
    ) = pipe(
        lambda course_id: get_course_lessons(course_id, session),
        lambda all_lessons: filter(
            lambda lesson: lesson["access_state"] == "available" and not lesson["is_locked"],
            all_lessons
        ),
        tuple,
        lambda available_lessons: map(
            lambda that_include: filter(
                lambda lesson: "available" in lesson[f"{that_include}_status"],
                available_lessons
            ), [
                "webinar",
                "homework",
                "conspect"
            ]
        ),
        lambda map_of_filters: map(tuple, map_of_filters)
    )(selected_course["resource_id"])

    options_check: Dict[str, List[str]] = prompt([
        {
            "type": "checkbox",
            "message": "What to fetch",
            "name": "actions",
            "choices": [
                {
                    "name": "Resources",
                    "checked": True
                },
                {
                    "name": "Homework"
                },
                {
                    "name": "Conspects"
                }
            ]
        }
    ])

    if "Resources" in options_check["actions"]:
        Logger.warn("Resources collection started")
        Logger.log("Fetching resources links...")

        resources_for_lessons: Tuple[Dict] = get_resources_for_lessons(
            selected_course["resource_id"],
            map(
                lambda obj: obj["webinar_id"],
                course_lessons_with_video
            ),
            session
        )

        paths: Iterable[Path] = build_dir_hierarchy(
            selected_course["name"],
            selected_course["subtitle"],
            selected_course["grades_range"],
            course_lessons_with_video
        )

        Logger.log("Downloading resources...")

        pool = Pool(cpu_count())
        pool.starmap(
            download_resources,
            map(
                lambda res_obj, path: [
                    {
                        **res_obj,
                        "destination": path
                    },
                    session
                ],
                resources_for_lessons,
                paths
            )
        )

        pool.close()
        pool.join()
        Logger.warn("Resources collection finished")

    coro_list = []
    semaphore = asyncio.Semaphore(2 if cpu_count() > 1 else 1)

    if "Homework" in options_check["actions"]:
        Logger.warn("Homework collection started")
        Logger.log("Collecting tasks...")

        lesson_tasks: Iterable[List[Dict]] = get_lesson_tasks(
            map(
                lambda obj: obj["id"],
                course_lessons_with_homework
            ),
            session
        )

        task_urls: Iterable[Iterable[str]] = construct_task_urls(
            map(
                lambda obj: obj["id"],
                course_lessons_with_homework
            ),
            lesson_tasks
        )

        paths: Iterable[Path] = build_dir_hierarchy(
            selected_course["name"],
            selected_course["subtitle"],
            selected_course["grades_range"],
            course_lessons_with_homework
        )

        Logger.warn(
            "Fetched tasks details. Homework collection will start soon..."
        )

        coro_list.extend(
            chain.from_iterable(
                map(
                    lambda url_tuple, path: map(
                        lambda url: save_page(
                            url,
                            path,
                            "homework",
                            map(
                                lambda item: {
                                    "name": item[0],
                                    "value": item[1],
                                    "domain": ".foxford.ru",
                                    "path": "/"
                                },
                                session.cookies.get_dict().items()
                            ),
                            semaphore
                        ),
                        url_tuple
                    ),
                    task_urls,
                    paths
                )
            )
        )

    if "Conspects" in options_check["actions"]:
        Logger.warn("Conspects collection started")

        conspect_urls: Iterable[Tuple[str]] = construct_conspect_urls(
            map(
                lambda obj: obj["id"],
                course_lessons_with_conspect
            ),
            map(
                lambda obj: obj["conspect_blocks_count"],
                course_lessons_with_conspect
            )
        )

        paths: Iterable[Path] = build_dir_hierarchy(
            selected_course["name"],
            selected_course["subtitle"],
            selected_course["grades_range"],
            course_lessons_with_conspect
        )

        Logger.warn(
            "Fetched conspects details. Conspects collection will start soon..."
        )

        coro_list.extend(
            chain.from_iterable(
                map(
                    lambda url_tuple, path: map(
                        lambda url: save_page(
                            url,
                            path,
                            "conspects",
                            map(
                                lambda item: {
                                    "name": item[0],
                                    "value": item[1],
                                    "domain": ".foxford.ru",
                                    "path": "/"
                                },
                                session.cookies.get_dict().items()
                            ),
                            semaphore
                        ),
                        url_tuple
                    ),
                    conspect_urls,
                    paths
                )
            )
        )

    if coro_list:
        Logger.warn("Actual collection started")

        asyncio.get_event_loop().run_until_complete(
            asyncio.wait(
                coro_list
            )
        )

        Logger.warn("Collection finished. Quitting...")
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.5))
        asyncio.get_event_loop().run_until_complete(terminate_browser_instance())


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--email", type=str, required=False)
    parser.add_argument("--password", type=str, required=False)

    args: Namespace = parser.parse_args()
    main(args.__dict__)
