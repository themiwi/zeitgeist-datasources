# identifier for the FF profile in which 'make install' installs this extension
TARGET_PROFILE = *default*

all: clean build

build:
	$(MAKE) --directory=src build

clean:
	-rm -f *.xpi
	$(MAKE) --directory=src clean

install: ;
	
uninstall: ;

local-install:
	cp Zeitgeist-nightly.xpi ~/.mozilla/firefox/$(TARGET_PROFILE)/extensions

local-uninstall:
	-rm -rf ~/.mozilla/firefox/$(TARGET_PROFILE)/extensions/zeitgeist\@zeitgeist-project.com
	-rm -rf ~/.mozilla/firefox/$(TARGET_PROFILE)/extensions/Zeitgeist-nightly.xpi
