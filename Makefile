FILENAME=zhwiki-20200501-all-titles-in-ns0

all: build

build: zhwiki.dict

download: $(FILENAME).gz

$(FILENAME).gz:
	wget https://dumps.wikimedia.org/zhwiki/20200501/$(FILENAME).gz

web-slang.source:
	./zhwiki-web-slang.py > web-slang.source

$(FILENAME): $(FILENAME).gz
	gzip -k -d $(FILENAME).gz

zhwiki.source: $(FILENAME) web-slang.source
	cat $(FILENAME) web-slang.source > zhwiki.source

zhwiki.raw: zhwiki.source
	./convert.py zhwiki.source > zhwiki.raw

zhwiki.dict: zhwiki.raw
	libime_pinyindict zhwiki.raw zhwiki.dict

install: zhwiki.dict
	install -Dm644 zhwiki.dict -t $(DESTDIR)/usr/share/fcitx5/pinyin/dictionaries/

clean:
	rm -f $(FILENAME) zhwiki.{source,raw,dict} web-slang.source
