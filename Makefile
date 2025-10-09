VERSION=20250820
WEB_SLANG_VERSION=20250823
ZHWIKI_FILENAME=zhwiki-$(VERSION)-all-titles-in-ns0
ZHDICT_FILENAME=zhwiktionary-$(VERSION)-all-titles-in-ns0
ZHSRC_FILENAME=zhwikisource-$(VERSION)-all-titles-in-ns0
WEB_SLANG_FILE=web-slang-$(WEB_SLANG_VERSION).txt
WEB_SLANG_SOURCE=web-slang-$(WEB_SLANG_VERSION).source

.DELETE_ON_ERROR:

all: build

build: zhwiki.dict zhwiktionary.dict zhwikisource.dict

download: $(ZHWIKI_FILENAME).gz

$(ZHWIKI_FILENAME).gz:
	wget https://dumps.wikimedia.org/zhwiki/$(VERSION)/$(ZHWIKI_FILENAME).gz

$(ZHDICT_FILENAME).gz:
	wget https://dumps.wikimedia.org/zhwiktionary/$(VERSION)/$(ZHDICT_FILENAME).gz

$(ZHSRC_FILENAME).gz:
	wget https://dumps.wikimedia.org/zhwikisource/$(VERSION)/$(ZHSRC_FILENAME).gz

$(WEB_SLANG_SOURCE):
	./zhwiki-web-slang.py --fetch > $(WEB_SLANG_SOURCE)

$(WEB_SLANG_FILE): $(WEB_SLANG_SOURCE)
	./zhwiki-web-slang.py --process $(WEB_SLANG_SOURCE) > $(WEB_SLANG_FILE)

$(ZHWIKI_FILENAME): $(ZHWIKI_FILENAME).gz
	gzip -k -d $(ZHWIKI_FILENAME).gz

$(ZHDICT_FILENAME): $(ZHDICT_FILENAME).gz
	gzip -k -d $(ZHDICT_FILENAME).gz

$(ZHSRC_FILENAME): $(ZHSRC_FILENAME).gz
	gzip -k -d $(ZHSRC_FILENAME).gz

zhwiki.source: $(ZHWIKI_FILENAME) $(WEB_SLANG_FILE)
	cat $(ZHWIKI_FILENAME) $(WEB_SLANG_FILE) > zhwiki.source

zhwiktionary.source: $(ZHDICT_FILENAME)
	cp $(ZHDICT_FILENAME) zhwiktionary.source

zhwikisource.source: $(ZHSRC_FILENAME)
	cp $(ZHSRC_FILENAME) zhwikisource.source

zhwiki.raw: zhwiki.source
	./convert.py zhwiki.source > zhwiki.raw.tmp
	sort -u zhwiki.raw.tmp > zhwiki.raw

zhwiktionary.raw: zhwiktionary.source
	./convert.py zhwiktionary.source > zhwiktionary.raw.tmp
	sort -u zhwiktionary.raw.tmp > zhwiktionary.raw

zhwikisource.raw: zhwikisource.source
	./convert.py zhwikisource.source > zhwikisource.raw.tmp
	sort -u zhwikisource.raw.tmp > zhwikisource.raw

zhwiki.dict: zhwiki.raw
	libime_pinyindict zhwiki.raw zhwiki.dict

zhwiktionary.dict: zhwiktionary.raw
	libime_pinyindict zhwiktionary.raw zhwiktionary.dict

zhwikisource.dict: zhwikisource.raw
	libime_pinyindict zhwikisource.raw zhwikisource.dict

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

zhwikisource.dict.yaml: zhwikisource.raw
	sed 's/[ ][ ]*/\t/g' zhwikisource.raw > zhwikisource.rime.raw
	sed -i 's/\t0//g' zhwikisource.rime.raw
	sed -i "s/'/ /g" zhwikisource.rime.raw
	printf -- '---\nname: zhwikisource\nversion: "0.1"\nsort: by_weight\n...\n' > zhwikisource.dict.yaml
	cat zhwikisource.rime.raw >> zhwikisource.dict.yaml

install-zhwiki: zhwiki.dict
	install -Dm644 zhwiki.dict -t $(DESTDIR)/usr/share/fcitx5/pinyin/dictionaries/

install_rime_dict-zhwiki: zhwiki.dict.yaml
	install -Dm644 zhwiki.dict.yaml -t $(DESTDIR)/usr/share/rime-data/

install-zhwiktionary: zhwiktionary.dict
	install -Dm644 zhwiktionary.dict -t $(DESTDIR)/usr/share/fcitx5/pinyin/dictionaries/

install_rime_dict-zhwiktionary: zhwiktionary.dict.yaml
	install -Dm644 zhwiktionary.dict.yaml -t $(DESTDIR)/usr/share/rime-data/

install-zhwikisource: zhwikisource.dict
	install -Dm644 zhwikisource.dict -t $(DESTDIR)/usr/share/fcitx5/pinyin/dictionaries/

install_rime_dict-zhwikisource: zhwikisource.dict.yaml
	install -Dm644 zhwikisource.dict.yaml -t $(DESTDIR)/usr/share/rime-data/

install: install-zhwiki install-zhwikidictionary install-zhwikisource

install_rime_dict: install_rime_dict-zhwiki install_rime_dict-zhwikidictionary install_rime_dict-zhwikisource

clean:
	rm -f $(ZHWIKI_FILENAME).gz $(WEB_SLANG_SOURCE) $(WEB_SLANG_FILE) $(ZHWIKI_FILENAME) zhwiki.source zhwiki.raw zhwiki.raw.tmp zhwiki.dict zhwiki.dict.yaml zhwiki.rime.raw
	rm -f $(ZHDICT_FILENAME).gz $(ZHDICT_FILENAME) zhwiktionary.source zhwiktionary.raw zhwiktionary.raw.tmp zhwiktionary.dict zhwiktionary.dict.yaml zhwiktionary.rime.raw
	rm -f $(ZHSRC_FILENAME).gz $(ZHSRC_FILENAME) zhwikisource.source zhwikisource.raw zhwikisource.raw.tmp zhwikisource.dict zhwikisource.dict.yaml zhwikisource.rime.raw
