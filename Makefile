VERSION=20200520
FILENAME=zhwiki-$(VERSION)-all-titles-in-ns0

all: build

build: zhwiki.dict

download: $(FILENAME).gz

$(FILENAME).gz:
	wget https://dumps.wikimedia.org/zhwiki/$(VERSION)/$(FILENAME).gz

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

zhwiki.dict.yaml: zhwiki.raw
	sed 's/[ ][ ]*/\t/g' zhwiki.raw > zhwiki.rime.raw
	sed -i 's/\t0//g' zhwiki.rime.raw
	sed -i "s/'/ /g" zhwiki.rime.raw
	echo -e '---\nname: zhwiki\nversion: "0.1"\nsort: by_weight\n...\n' >> zhwiki.dict.yaml
	cat zhwiki.rime.raw >> zhwiki.dict.yaml

install: zhwiki.dict
	install -Dm644 zhwiki.dict -t $(DESTDIR)/usr/share/fcitx5/pinyin/dictionaries/

install_rime_dict: zhwiki.dict.yaml
	install -Dm644 zhwiki.dict.yaml -t $(DESTDIR)/usr/share/rime-data/

clean:
	rm -f $(FILENAME) zhwiki.{source,raw,dict,dict.yaml} web-slang.source
