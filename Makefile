VERSION=20250820
WEB_SLANG_VERSION=20250823
ZHWIKI_FILENAME=zhwiki-$(VERSION)-all-titles-in-ns0
ZHDICT_FILENAME=zhwiktionary-$(VERSION)-all-titles-in-ns0
ZHSRC_FILENAME=zhwikisource-$(VERSION)-all-titles-in-ns0
WEB_SLANG_FILE=web-slang-$(WEB_SLANG_VERSION).txt
WEB_SLANG_SOURCE=web-slang-$(WEB_SLANG_VERSION).wikitext
ZHWIKI_EXCLUDE_TITLES_VERSION=20251010
ZHWIKI_EXCLUDE_TITLES_FILE=zhwiki-exclude-titles-$(ZHWIKI_EXCLUDE_TITLES_VERSION).txt

.DELETE_ON_ERROR:

all: build

build: zhwiki.dict zhwiktionary.dict zhwikisource.dict web-slang.dict

build_rime_dict: zhwiki.dict.yaml zhwiktionary.dict.yaml zhwikisource.dict.yaml web-slang.dict.yaml

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

$(ZHWIKI_EXCLUDE_TITLES_FILE):
	./zhwiki-exclude-titles.py --save $@

%: %.gz
	gzip -k -d $<

zhwiki.source: $(ZHWIKI_FILENAME)
	cp $< $@

zhwiktionary.source: $(ZHDICT_FILENAME)
	cp $< $@

zhwikisource.source: $(ZHSRC_FILENAME)
	cp $< $@

web-slang.source: $(WEB_SLANG_FILE)
	cp $< $@

zhwiki-exclude.txt: $(ZHWIKI_EXCLUDE_TITLES_FILE)
	cp $< $@

zhwiktionary-exclude.txt:
	touch $@

zhwikisource-exclude.txt:
	touch $@

%.raw: %.source %-exclude.txt
	./convert.py $< $*-exclude.txt > $@.tmp
	sort -u $@.tmp > $@

%.dict: %.raw
	libime_pinyindict $< $@

%.dict.yaml: %.raw
	sed 's/[ ][ ]*/\t/g' $< > $*.rime.raw
	sed -i 's/\t0//g' $*.rime.raw
	sed -i "s/'/ /g" $*.rime.raw
	printf -- '---\nname: $*\nversion: "0.1"\nsort: by_weight\n...\n' > $@
	cat $*.rime.raw >> $@

install-%: %.dict
	install -Dm644 $< -t $(DESTDIR)/usr/share/fcitx5/pinyin/dictionaries/

install_rime_dict-%: %.dict.yaml
	install -Dm644 $< -t $(DESTDIR)/usr/share/rime-data/

install: install-zhwiki install-zhwiktionary install-zhwikisource install-web-slang

install_rime_dict: install_rime_dict-zhwiki install_rime_dict-zhwiktionary install_rime_dict-zhwikisource install_rime_dict-web-slang

clean:
	rm -f $(ZHWIKI_FILENAME).gz $(ZHWIKI_FILENAME) zhwiki.source zhwiki.raw zhwiki.raw.tmp zhwiki.dict zhwiki.dict.yaml zhwiki.rime.raw
	rm -f $(ZHDICT_FILENAME).gz $(ZHDICT_FILENAME) zhwiktionary.source zhwiktionary.raw zhwiktionary.raw.tmp zhwiktionary.dict zhwiktionary.dict.yaml zhwiktionary.rime.raw
	rm -f $(ZHSRC_FILENAME).gz $(ZHSRC_FILENAME) zhwikisource.source zhwikisource.raw zhwikisource.raw.tmp zhwikisource.dict zhwikisource.dict.yaml zhwikisource.rime.raw
	rm -f $(WEB_SLANG_SOURCE) $(WEB_SLANG_FILE) web-slang.source web-slang.raw web-slang.raw.tmp web-slang.dict web-slang.dict.yaml web-slang.rime.raw
	rm -f ${ZHWIKI_EXCLUDE_TITLES_FILE} zhwiki-exclude-titles-*.txt zhwiki-exclude.txt zhwiktionary-exclude.txt zhwikisource-exclude.txt
