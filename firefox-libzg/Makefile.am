SUBDIRS = extension

# identifier for the FF profile in which 'make install' installs this extension
TARGET_PROFILE = *default*

local-install: all
	$(MAKE) -C extension $@
	unzip -o ZeitgeistDataprovider.xpi -d ~/xpcom_firefox\@zeitgeist-project.com
	cd ~/.mozilla/firefox/$(TARGET_PROFILE)/ && mkdir extensions
	cp -r ~/xpcom_firefox\@zeitgeist-project.com/ ~/.mozilla/firefox/$(TARGET_PROFILE)/extensions/

local-uninstall:
	$(MAKE) -C extension $@
	-rm -rf ~/.mozilla/firefox/$(TARGET_PROFILE)/extensions/xpcom_firefox\@zeitgeist-project.com
	-rm -rf ~/.mozilla/firefox/$(TARGET_PROFILE)/extensions/ZeitgeistDataprovider.xpi

