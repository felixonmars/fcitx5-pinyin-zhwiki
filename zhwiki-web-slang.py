#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.parse
import urllib.request

_ZHWIKI_SOURCE_URL = "https://zh.wikipedia.org/w/api.php?action=parse&format=json&prop=wikitext&uselang=zh&formatversion=2&page="
_PAGE = "中国大陆网络用语列表"

page = urllib.request.urlopen(_ZHWIKI_SOURCE_URL + urllib.parse.quote(_PAGE)).read()
wikitext = json.loads(page)["parse"]["wikitext"]
words = set()


def add_word(word):
    if word.startswith("形容"):
        return
    for garbage in ("、", "[", "]", "…"):
        word = word.replace(garbage, "")
    words.add(word.strip())


def add_words(word):
    for word_separator in ("、", "/", "|", "，", "。"):
        if word_separator in word:
            for w in word.split(word_separator):
                # recursively resolve
                add_words(w.strip())
            break
    else:
        add_word(word)


for line in wikitext.split("\n"):
    if line.startswith("*"):
        # Lists
        for table_separator in ("：", ":"):
            if table_separator in line:
                word = line.split(table_separator)[0].strip("*").strip()
                add_words(word)
                break
    elif line.startswith("|"):
        # Tables
        word = line.split("|")[1]
        add_words(word)

for word in words:
    print(word)
