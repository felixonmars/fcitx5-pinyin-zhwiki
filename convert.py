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


def make_output(word, pinyin):
    return '\t'.join([word, pinyin, '0'])


def main():
    previous_title = None
    result_count = 0
    with open(sys.argv[1]) as f:
        for line in f:
            title = _TO_SIMPLIFIED_CHINESE.convert(line.strip())
            if is_good_title(title, previous_title):
                pinyin = _PINYIN_SEPARATOR.join(lazy_pinyin(title))
                if pinyin == title:
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
