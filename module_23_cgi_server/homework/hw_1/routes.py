import json
from http import HTTPStatus
from urllib.parse import unquote


def json_response(start_response, status: HTTPStatus, data: dict) -> list[bytes]:
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")

    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]

    start_response(
        f"{status.value} {status.phrase}",
        headers
    )

    return [body]


def application(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = unquote(environ.get("PATH_INFO", "/"))

    if method != "GET":
        return json_response(
            start_response,
            HTTPStatus.METHOD_NOT_ALLOWED,
            {
                "error": "method not allowed",
                "allowed_method": "GET"
            }
        )

    if path == "/hello":
        return json_response(
            start_response,
            HTTPStatus.OK,
            {
                "message": "hello",
                "name": "username"
            }
        )

    if path.startswith("/hello/"):
        username = path.removeprefix("/hello/")

        if username and "/" not in username:
            return json_response(
                start_response,
                HTTPStatus.OK,
                {
                    "message": "hello",
                    "name": username
                }
            )

    return json_response(
        start_response,
        HTTPStatus.NOT_FOUND,
        {
            "error": "not found"
        }
    )