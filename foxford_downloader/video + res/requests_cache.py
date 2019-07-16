from functools import lru_cache

from requests import Response, Session
from requests.adapters import HTTPAdapter
from requests.cookies import cookiejar_from_dict, extract_cookies_to_jar
from requests.structures import CaseInsensitiveDict
from requests.utils import get_encoding_from_headers


class CachedResponse(Response):
    @property
    @lru_cache(maxsize=1, typed=False)
    def content(self):
        return super().content

    @property
    @lru_cache(maxsize=1, typed=False)
    def text(self):
        return super().text

    @lru_cache(maxsize=1, typed=False)
    def json(self, **kwargs):
        return super().json(**kwargs)


class CacheHTTPAdapter(HTTPAdapter):
    def build_response(self, req, resp):
        response = CachedResponse()
        response.status_code = getattr(resp, "status", None)
        response.headers = CaseInsensitiveDict(getattr(resp, "headers", {}))
        response.encoding = get_encoding_from_headers(response.headers)
        response.raw = resp
        response.reason = resp.reason

        if isinstance(req.url, bytes):
            response.url = req.url.decode("utf-8")
        else:
            response.url = req.url

        extract_cookies_to_jar(response.cookies, req, resp)
        response.request = req
        response.connection = self
        return response


class CachedSession():
    def __new__(self):
        s = Session()
        a = CacheHTTPAdapter(max_retries=3)
        s.mount("http://", a)
        s.mount("https://", a)
        return s
