#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.parse
import urllib.request
import collections
import sys


def fetch():
    _ZHWIKI_SOURCE_URL = "https://zh.wikipedia.org/w/api.php?action=parse&format=json&prop=wikitext&uselang=zh&formatversion=2&page="
    _PAGE = "中国大陆网络用语列表"

    page = urllib.request.urlopen(_ZHWIKI_SOURCE_URL + urllib.parse.quote(_PAGE)).read()
    wikitext = json.loads(page)["parse"]["wikitext"]
    return wikitext


def trim_templates(wikitext):
    template_level = 0
    new_wikitext = ""
    while True:
        assert template_level >= 0, ValueError("Unbalanced template in wikitext:\n" + wikitext)
        pre_open, open_tag, post_open = wikitext.partition("{{")
        pre_close, close_tag, post_close = wikitext.partition("}}")
        if open_tag and (not close_tag or len(pre_open) < len(pre_close)):
            # Template starts here ({{)
            wikitext = post_open
            if template_level == 0:
                new_wikitext += pre_open
            template_level += 1
        elif close_tag:
            # Template ends here (}})
            wikitext = post_close
            template_level -= 1
        else:
            # No more templates
            assert template_level == 0, ValueError("Unbalanced template in wikitext:\n" + wikitext)
            # The assertion below must be true on earth
            assert open_tag == close_tag == "", RuntimeError("Cosmic radiation detected")
            new_wikitext += wikitext
            break

    return new_wikitext


def process(wikitext):
    wikitext = trim_templates(wikitext)
    words = collections.OrderedDict()

    def add_word(word):
        for garbage in ("[", "]", "…", ":", "：", ")", "）", '"', "“", "”", "-{", "}-", "简称", "簡稱"):
            word = word.replace(garbage, "")
        words[word.strip()] = None

    def add_words(word):
        for word_separator in ("、", "/", "|", "，", "。", "?", "？", "(", "（"):
            if word_separator in word:
                for w in word.split(word_separator):
                    # recursively resolve
                    add_words(w.strip())
                break
        else:
            add_word(word)

    def iter_bolds(line):
        line_bak = line
        while "'''" in line:
            _, sep1, line = line.partition("'''")
            bold, sep2, line = line.partition("'''")
            assert sep1 and sep2, ValueError("Unclosed ''' in line: " + line_bak)
            yield bold

    for line in wikitext.split("\n"):
        if not line.startswith("*"):
            continue
        # Lists
        line = line.strip("*").strip()
        pre_colon, sep, post_colon = line.partition("'''：")
        if not sep:
            pre_colon, sep, post_colon = line.partition("''':")
        for bold in iter_bolds(pre_colon + sep):
            # Add bold words before colon
            add_words(bold)
        for bold in iter_bolds(post_colon):
            # Add bold words after colon (or line w/o colon), skipping the origin of abbreviation (length probably <= 2)
            if len(bold) > 2:
                add_words(bold)

    return words


def print_words(words):
    for word in words:
        print(word)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        wikitext = fetch()
        words = process(wikitext)
        print_words(words)

    elif sys.argv[1] == "--fetch":
        print(fetch())

    elif sys.argv[1] == "--process":
        wikitext = open(sys.argv[2]).read()
        print_words(process(wikitext))

    else:
        raise NotImplementedError
