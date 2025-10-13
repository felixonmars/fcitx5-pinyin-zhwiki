#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Usage:
#   convert.py input_filename [exclude_file]
# input_filename is a file of Wikipedia article titles, one title per line.
# exclude_file is an optional file of titles to exclude, one title per line.

import logging
import os.path
import regex
import sys

import opencc
from pypinyin import lazy_pinyin

# Require at least 2 characters
_MINIMUM_LEN = 2
_LIST_PAGE_ENDINGS = [
    '列表',
    '对照表',
]
_LOG_EVERY = 1000

_PINYIN_SEPARATOR = '\''
# https://ayaka.shn.hk/hanregex/
# INTERPUNCT   \u00b7 -> ·
# HYPHEN-MINUS \u002d -> -
# HYPHEN       \u2010 -> ‐
# EN DASH      \u2013 -> –
# EM DASH      \u2014 -> —
_HANZI_RE = regex.compile(r"([\p{Unified_Ideograph}\u3006\u3007\u00b7\u002d\u2010\u2013\u2014][\ufe00-\ufe0f\U000e0100-\U000e01ef]?)+")
_INTERPUNCT_TRANSTAB = str.maketrans("", "", "·-‐–—")
_TO_SIMPLIFIED_CHINESE = opencc.OpenCC('t2s.json')

_PINYIN_FIXES = {
    'n': 'en',  # https://github.com/felixonmars/fcitx5-pinyin-zhwiki/issues/13
}

logging.basicConfig(level=logging.INFO)


def is_good_title(title, previous_title=None):
    if not _HANZI_RE.fullmatch(title):
        return False

    # Skip single character & too long pages
    if len(title) < _MINIMUM_LEN:
        return False

    # Skip list pages
    if title.endswith(tuple(_LIST_PAGE_ENDINGS)):
        return False

    if previous_title and \
      len(previous_title) >= 4 and \
      title.startswith(previous_title):
        return False

    return True


def log_count(count):
    logging.info(f'{count} words generated')


def make_output(word, pinyin):
    return '\t'.join([word, pinyin, '0'])


def load_excluded_titles(filename="exclude-titles.txt"):
    excluded_titles = set()
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                excluded_titles.add(line.strip())
        logging.info(f'Loaded {len(excluded_titles)} excluded titles from {filename}')
    else:
        logging.info(f'No excluded titles file found at {filename}, continuing without exclusions')
    return excluded_titles


def main():
    source = sys.argv[1]
    exclude_filename = sys.argv[2] if len(sys.argv) >= 3 else None

    previous_title = None
    result_count = 0

    excluded_titles = load_excluded_titles(exclude_filename) if exclude_filename else None

    with open(source) as f:
        for line in f:
            title = _TO_SIMPLIFIED_CHINESE.convert(line.strip())
            if excluded_titles and title in excluded_titles:
                logging.debug(f'Excluded title: {title}')
                continue
            if is_good_title(title, previous_title):
                stripped_title = title.translate(_INTERPUNCT_TRANSTAB)
                pinyin = [_PINYIN_FIXES.get(item, item) for item in lazy_pinyin(stripped_title)]
                pinyin = _PINYIN_SEPARATOR.join(pinyin)
                if _HANZI_RE.search(pinyin):
                    logging.info(
                        f'Failed to convert to Pinyin. Ignoring: {pinyin}')
                    continue
                print(make_output(title, pinyin))
                result_count += 1
                if result_count % _LOG_EVERY == 0:
                    log_count(result_count)
                previous_title = title
    log_count(result_count)


if __name__ == '__main__':
    main()
