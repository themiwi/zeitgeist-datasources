SUBDIRS = components

xul_extdir = $(datadir)/xul-ext-zeitgeist
xul_ext_DATA = \
	defaults \
	chrome \
	license.txt \
	chrome.manifest \
	install.rdf \
	components/zeitgeist.xpt \
	$(NULL)


# we want to allow also local install
EXTENSION_CONTENT = \
	$(xul_ext_DATA) \
	components/libzeitgeist_xpcom.so \
	$(NULL)

local-install: all
	$(MAKE) -C components $@
	zip -r ../ZeitgeistDataprovider.xpi $(EXTENSION_CONTENT)

local-uninstall:
	$(MAKE) -C components $@
