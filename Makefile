VERSION=20250820
WEB_SLANG_VERSION=20250823
ZHWIKI_FILENAME=zhwiki-$(VERSION)-all-titles-in-ns0
ZHDICT_FILENAME=zhwiktionary-$(VERSION)-all-titles-in-ns0
WEB_SLANG_FILE=web-slang-$(WEB_SLANG_VERSION).txt
WEB_SLANG_SOURCE=web-slang-$(WEB_SLANG_VERSION).source

.DELETE_ON_ERROR:

all: build

build: zhwiki.dict zhwiktionary.dict

download: $(ZHWIKI_FILENAME).gz

$(ZHWIKI_FILENAME).gz:
	wget https://dumps.wikimedia.org/zhwiki/$(VERSION)/$(ZHWIKI_FILENAME).gz

$(ZHDICT_FILENAME).gz:
	wget https://dumps.wikimedia.org/zhwiktionary/$(VERSION)/$(ZHDICT_FILENAME).gz

$(WEB_SLANG_SOURCE):
	./zhwiki-web-slang.py --fetch > $(WEB_SLANG_SOURCE)

$(WEB_SLANG_FILE): $(WEB_SLANG_SOURCE)
	./zhwiki-web-slang.py --process $(WEB_SLANG_SOURCE) > $(WEB_SLANG_FILE)

$(ZHWIKI_FILENAME): $(ZHWIKI_FILENAME).gz
	gzip -k -d $(ZHWIKI_FILENAME).gz

$(ZHDICT_FILENAME): $(ZHDICT_FILENAME).gz
	gzip -k -d $(ZHDICT_FILENAME).gz

zhwiki.source: $(ZHWIKI_FILENAME) $(WEB_SLANG_FILE)
	cat $(ZHWIKI_FILENAME) $(WEB_SLANG_FILE) > zhwiki.source

zhwiktionary.source: $(ZHDICT_FILENAME)
	cp $(ZHDICT_FILENAME) zhwiktionary.source

zhwiki.raw: zhwiki.source
	./convert.py zhwiki.source > zhwiki.raw.tmp
	sort -u zhwiki.raw.tmp > zhwiki.raw

zhwiktionary.raw: zhwiktionary.source
	./convert.py zhwiktionary.source > zhwiktionary.raw.tmp
	sort -u zhwiktionary.raw.tmp > zhwiktionary.raw

zhwiki.dict: zhwiki.raw
	libime_pinyindict zhwiki.raw zhwiki.dict

zhwiktionary.dict: zhwiktionary.raw
	libime_pinyindict zhwiktionary.raw zhwiktionary.dict

zhwiki.dict.yaml: zhwiki.raw
	sed 's/[ ][ ]*/\t/g' zhwiki.raw > zhwiki.rime.raw
	sed -i 's/\t0//g' zhwiki.rime.raw
	sed -i "s/'/ /g" zhwiki.rime.raw
	printf -- '---\nname: zhwiki\nversion: "0.1"\nsort: by_weight\n...\n' > zhwiki.dict.yaml
	cat zhwiki.rime.raw >> zhwiki.dict.yaml

zhwiktionary.dict.yaml: zhwiktionary.raw
	sed 's/[ ][ ]*/\t/g' zhwiktionary.raw > zhwiktionary.rime.raw
	sed -i 's/\t0//g' zhwiktionary.rime.raw
	sed -i "s/'/ /g" zhwiktionary.rime.raw
	printf -- '---\nname: zhwiktionary\nversion: "0.1"\nsort: by_weight\n...\n' > zhwiktionary.dict.yaml
	cat zhwiktionary.rime.raw >> zhwiktionary.dict.yaml

install-zhwiki: zhwiki.dict
	install -Dm644 zhwiki.dict -t $(DESTDIR)/usr/share/fcitx5/pinyin/dictionaries/

install_rime_dict-zhwiki: zhwiki.dict.yaml
	install -Dm644 zhwiki.dict.yaml -t $(DESTDIR)/usr/share/rime-data/

install-zhwiktionary: zhwiktionary.dict
	install -Dm644 zhwiktionary.dict -t $(DESTDIR)/usr/share/fcitx5/pinyin/dictionaries/

install_rime_dict-zhwiktionary: zhwiktionary.dict.yaml
	install -Dm644 zhwiktionary.dict.yaml -t $(DESTDIR)/usr/share/rime-data/

install: install-zhwiki install-zhwiktionary

install_rime_dict: install_rime_dict-zhwiki install_rime_dict-zhwiktionary

clean:
	rm -f $(ZHWIKI_FILENAME).gz $(WEB_SLANG_SOURCE) $(WEB_SLANG_FILE) $(ZHWIKI_FILENAME) zhwiki.source zhwiki.raw zhwiki.raw.tmp zhwiki.dict zhwiki.dict.yaml zhwiki.rime.raw
	rm -f $(ZHDICT_FILENAME).gz $(ZHDICT_FILENAME) zhwiktionary.source zhwiktionary.raw zhwiktionary.raw.tmp zhwiktionary.dict zhwiktionary.dict.yaml zhwiktionary.rime.raw
