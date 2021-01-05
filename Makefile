VERSION=20210101
FILENAME=zhwiki-$(VERSION)-all-titles-in-ns0
WEB_SLANG_FILE=web-slang-$(VERSION).source

all: build

build: zhwiki.dict

download: $(FILENAME).gz

$(FILENAME).gz:
	wget https://dumps.wikimedia.org/zhwiki/$(VERSION)/$(FILENAME).gz

$(WEB_SLANG_FILE):
	./zhwiki-web-slang.py > $(WEB_SLANG_FILE)

$(FILENAME): $(FILENAME).gz
	gzip -k -d $(FILENAME).gz

zhwiki.source: $(FILENAME) $(WEB_SLANG_FILE)
	cat $(FILENAME) $(WEB_SLANG_FILE) > zhwiki.source

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
