#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Usage:
#   exclude-titles.py output_filename
# output_filename is the file to save the excluded titles, one title per line.

import requests
import opencc
import sys

_TO_SIMPLIFIED_CHINESE = opencc.OpenCC("t2s.json")


def fetch_excluded_titles():
    excluded_titles = set()
    category = "Category:錯字重定向"
    url = "https://zh.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": "max",
    }
    while True:
        response = requests.get(url, params=params)
        data = response.json()
        members = data.get("query", {}).get("categorymembers", [])
        for member in members:
            excluded_titles.add(_TO_SIMPLIFIED_CHINESE.convert(member["title"]))
        if "continue" in data:
            params.update(data["continue"])
        else:
            break
    return excluded_titles


def save_excluded_titles(filename):
    excluded_titles = fetch_excluded_titles()
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(title + "\n" for title in excluded_titles)


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "exclude-titles.txt"
    save_excluded_titles(output)
