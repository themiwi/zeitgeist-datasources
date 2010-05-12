
# identifier for the FF profile in which 'make install' installs this extension
TARGET_PROFILE = *default*

all: clean build

build:
	$(MAKE) --directory=extension build

clean:
	-rm -f *.xpi
	$(MAKE) --directory=extension clean

install: ;
	
uninstall: ;

local-install:
	cp ZeitgeistDataprovider.xpi ~/.mozilla/firefox/$(TARGET_PROFILE)/extensions

local-uninstall:
	-rm -rf ~/.mozilla/firefox/$(TARGET_PROFILE)/extensions/xpcom_firefox\@zeitgeist-project.com
	-rm -rf ~/.mozilla/firefox/$(TARGET_PROFILE)/extensions/ZeitgeistDataprovider.xpi
