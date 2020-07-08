#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Usage:
#   convert.py input_filename
# input_filename is a file of Wikipedia article titles, one title per line.

import logging
import re
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
_HANZI_RE = re.compile('^[\u4e00-\u9fa5]+$')
_TO_SIMPLIFIED_CHINESE = opencc.OpenCC('t2s.json')

logging.basicConfig(level=logging.INFO)


def is_good_title(title, previous_title=None):
    if not _HANZI_RE.match(title):
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


def process(convert_title, title_to_line):
    previous_title = None
    result_count = 0
    with open(sys.argv[1]) as f:
        for line in f:
            title = convert_title(line.strip())
            if is_good_title(title, previous_title):
                line = title_to_line(title)
                if line is not None:
                    print(line)
                result_count += 1
                if result_count % _LOG_EVERY == 0:
                    log_count(result_count)
                previous_title = title
    log_count(result_count)


def main():
    if sys.argv[2] == '--rime':
        process(
            convert_title=lambda it: it,
            title_to_line=lambda it: it
        )
    else:
        def title_to_line(title):
            pinyin = _PINYIN_SEPARATOR.join(lazy_pinyin(title))
            if pinyin == title:
                logging.info(
                    f'Failed to convert to Pinyin. Ignoring: {pinyin}')
                return None
            return '\t'.join([title, pinyin, '0'])
        process(
            convert_title=lambda it: _TO_SIMPLIFIED_CHINESE.convert(it),
            title_to_line=title_to_line
        )


if __name__ == '__main__':
    main()
