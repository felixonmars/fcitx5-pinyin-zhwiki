#!/bin/python
import sys
import re
import opencc
from pypinyin import lazy_pinyin
converter = opencc.OpenCC('t2s.json')

FILE = sys.argv[1]

HANZI_RE = re.compile('^[\u4e00-\u9fa5]+$')
count = 0
with open(FILE) as f:
    for line in f:
        line = line.rstrip("\n")
        if not HANZI_RE.match(line):
            continue

        # Skip single character & too long pages
        if not 1 < len(line) < 9:
            continue

        # Skip list pages
        if line.endswith('\u5217\u8868'):
            continue

        pinyin = "'".join(lazy_pinyin(line))
        if pinyin == line:
            print("Failed to convert, ignoring:", pinyin, file=sys.stderr)
            continue

        print("\t".join((converter.convert(line), pinyin, "0")))
        count += 1
        if count % 1000 == 0:
            print(str(count) + " converted", file=sys.stderr)

if count % 1000 != 0:
    print(str(count) + " converted", file=sys.stderr)
