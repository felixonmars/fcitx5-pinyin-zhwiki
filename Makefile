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

build_rime_dict: zhwiki.dict.yaml zhwiktionary.dict.yaml zhwikisource.dict.yaml

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

%: %.gz
	gzip -k -d $<

zhwiki.source: $(ZHWIKI_FILENAME) $(WEB_SLANG_FILE)
	cat $? > $@

zhwiktionary.source: $(ZHDICT_FILENAME)
	cp $< $@

zhwikisource.source: $(ZHSRC_FILENAME)
	cp $< $@

%.raw: %.source
	./convert.py $< > $@.tmp
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

install: install-zhwiki install-zhwikidictionary install-zhwikisource

install_rime_dict: install_rime_dict-zhwiki install_rime_dict-zhwikidictionary install_rime_dict-zhwikisource

clean:
	rm -f $(ZHWIKI_FILENAME).gz $(WEB_SLANG_SOURCE) $(WEB_SLANG_FILE) $(ZHWIKI_FILENAME) zhwiki.source zhwiki.raw zhwiki.raw.tmp zhwiki.dict zhwiki.dict.yaml zhwiki.rime.raw
	rm -f $(ZHDICT_FILENAME).gz $(ZHDICT_FILENAME) zhwiktionary.source zhwiktionary.raw zhwiktionary.raw.tmp zhwiktionary.dict zhwiktionary.dict.yaml zhwiktionary.rime.raw
	rm -f $(ZHSRC_FILENAME).gz $(ZHSRC_FILENAME) zhwikisource.source zhwikisource.raw zhwikisource.raw.tmp zhwikisource.dict zhwikisource.dict.yaml zhwikisource.rime.raw
