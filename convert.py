#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Usage:
#   convert.py input_filename
# input_filename is a file of Wikipedia article titles, one title per line.

import logging
import regex
import sys
import unicodedata

import opencc
from pypinyin import lazy_pinyin
from more_itertools import collapse, flatten

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
_CONVERTABLE_RE = regex.compile(r"([\p{Unified_Ideograph}\u3006\u3007\u00b7\u002d\u2010\u2013\u2014][\ufe00-\ufe0f\U000e0100-\U000e01ef]?|[a-zA-Z\p{Greek}])+")
_HANZI_RE = regex.compile(r"([\p{Unified_Ideograph}\u3006\u3007\u00b7\u002d\u2010\u2013\u2014][\ufe00-\ufe0f\U000e0100-\U000e01ef]?)+")
_BOUND_RE = regex.compile(r"(?<=[\p{Unified_Ideograph}\u3006\u3007\u00b7\u002d\u2010\u2013\u2014][\ufe00-\ufe0f\U000e0100-\U000e01ef]?)(?=[a-zA-Z\p{Greek}])|(?<=[a-zA-Z\p{Greek}])(?=[\p{Unified_Ideograph}\u3006\u3007\u00b7\u002d\u2010\u2013\u2014][\ufe00-\ufe0f\U000e0100-\U000e01ef]?)")
_INTERPUNCT_TRANSTAB = str.maketrans("", "", "·-‐–—")
_TO_SIMPLIFIED_CHINESE = opencc.OpenCC('t2s.json')

_PINYIN_FIXES = {
    'n': 'en',  # https://github.com/felixonmars/fcitx5-pinyin-zhwiki/issues/13
}

_GREEK2LATIN = {
    u'\u0391': ['A', 'L', 'P', 'ha'],          # Alpha
    u'\u0392': ['B', 'E', 'ta'],               # Beta
    u'\u0393': ['ga', 'M', 'ma'],              # Gamma
    u'\u0394': ['de', 'L', 'ta'],              # Delta
    u'\u0395': ['E', 'P', 'si', 'L', 'O', 'N'],# Epsilon
    u'\u0396': ['ze', 'ta'],                   # Zeta
    u'\u0397': ['E', 'ta'],                    # Eta
    u'\u0398': ['T', 'he', 'ta'],              # Theta
    u'\u0399': ['I', 'O', 'ta'],               # Iota
    u'\u039A': ['ka', 'P', 'pa'],              # Kappa
    u'\u039B': ['la', 'M', 'B', 'da'],         # Lambda
    u'\u039C': ['mu'],                         # Mu
    u'\u039D': ['nu'],                         # Nu
    u'\u039E': ['xi'],                         # Xi
    u'\u039F': ['O', 'mi', 'C', 'R', 'O', 'N'],# Omicron
    u'\u03A0': ['pi'],                         # Pi
    u'\u03A1': ['R', 'H', 'O'],                # Rho
    u'\u03A3': ['si', 'G', 'ma'],              # Sigma
    u'\u03A4': ['ta', 'U'],                    # Tau
    u'\u03A5': ['U', 'P', 'si', 'L', 'O', 'N'],# Upsilon
    u'\u03A6': ['P', 'hi'],                    # Phi
    u'\u03A7': ['C', 'hi'],                    # Chi
    u'\u03A8': ['P', 'si'],                    # Psi
    u'\u03A9': ['O', 'me', 'ga'],              # Omega
    u'\u03B1': ['A', 'L', 'P', 'ha'],          # alpha
    u'\u03B2': ['B', 'E', 'ta'],               # beta
    u'\u03B3': ['ga', 'M', 'ma'],              # gamma
    u'\u03B4': ['de', 'L', 'ta'],              # delta
    u'\u03B5': ['E', 'P', 'si', 'L', 'O', 'N'],# epsilon
    u'\u03B6': ['ze', 'ta'],                   # zeta
    u'\u03B7': ['E', 'ta'],                    # eta
    u'\u03B8': ['T', 'he', 'ta'],              # theta
    u'\u03B9': ['I', 'O', 'ta'],               # iota
    u'\u03BA': ['ka', 'P', 'pa'],              # kappa
    u'\u03BB': ['la', 'M', 'B', 'da'],         # lambda
    u'\u03BC': ['mu'],                         # mu
    u'\u03BD': ['nu'],                         # nu
    u'\u03BE': ['xi'],                         # xi
    u'\u03BF': ['O', 'mi', 'C', 'R', 'O', 'N'],# omicron
    u'\u03C0': ['pi'],                         # pi
    u'\u03C1': ['R', 'H', 'O'],                # rho
    u'\u03C3': ['si', 'G', 'ma'],              # sigma
    u'\u03C4': ['ta', 'U'],                    # tau
    u'\u03C5': ['U', 'P', 'si', 'L', 'O', 'N'],# upsilon
    u'\u03C6': ['P', 'hi'],                    # phi
    u'\u03C7': ['C', 'hi'],                    # chi
    u'\u03C8': ['P', 'si'],                    # psi
    u'\u03C9': ['O', 'me', 'ga'],              # omega

    # NFD of final sigma is itself
    u'\u03C2': ['si', 'G', 'ma'],              # final sigma
}

logging.basicConfig(level=logging.INFO)


def is_good_title(title, previous_title=None):
    if not _CONVERTABLE_RE.fullmatch(title):
        return False

    # At least have one Hanzi character
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

def map_to_libime_compatible_fmt(s):
    if _HANZI_RE.fullmatch(s):
        yield from [_PINYIN_FIXES.get(item, item) for item in lazy_pinyin(s)]
    else:
        # NFD of Greek letter is basic alphabet + modifier, so the first char is basic alphabet. e.g. ἁ (ἁ) -> α + ̔
        yield from [_GREEK2LATIN.get(unicodedata.normalize('NFD', item)[0], item.upper()) for item in s]

def main():
    previous_title = None
    result_count = 0
    with open(sys.argv[1]) as f:
        for line in f:
            title = _TO_SIMPLIFIED_CHINESE.convert(line.strip())
            if is_good_title(title, previous_title):
                stripped_title = title.translate(_INTERPUNCT_TRANSTAB)
                pinyins = [map_to_libime_compatible_fmt(s) for s in regex.split(_BOUND_RE, stripped_title) if s]
                pinyin = _PINYIN_SEPARATOR.join(collapse(pinyins))
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
