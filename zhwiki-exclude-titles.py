#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import sys
from mediawiki import init_session, do_request


def fetch():
    # https://www.mediawiki.org/wiki/API:Categorymembers
    _API_URL = "https://zh.wikipedia.org/w/api.php"
    _CATEGORY_TITLE = "Category:錯字重定向"

    init_session()
    titles = collections.OrderedDict()
    base_params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": _CATEGORY_TITLE,
        "cmlimit": "max",
        "cmprop": "title",
    }
    continuation = {}

    while True:
        query_params = {**base_params, **continuation}
        response = do_request(_API_URL, params=query_params)
        payload = response.json()
        members = payload.get("query", {}).get("categorymembers", [])
        for member in members:
            titles[member["title"]] = None  # Ordered set behaviour

        continuation = payload.get("continue")
        if not continuation:
            break

    return list(titles.keys())


def print_titles(titles):
    for title in titles:
        print(title)


def save_titles(path, titles):
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(title + "\n" for title in titles)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_titles(fetch())

    elif sys.argv[1] == "--fetch":
        print_titles(fetch())

    elif sys.argv[1] == "--save":
        if len(sys.argv) < 3:
            raise ValueError("Missing path for --save")
        save_titles(sys.argv[2], fetch())

    else:
        raise NotImplementedError
