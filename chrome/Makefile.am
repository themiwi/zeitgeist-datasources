chromeresourcedir = $(DESTDIR)/opt/google/chrome/resources/zeitgeist-plugin
chromeresource_DATA = \
	background.html \
	content_script.js \
	manifest.json \
	zeitgeist.js

pluginbinarydir = $(chromeresourcedir)/plugin
pluginbinary_LTLIBRARIES = libzeitgeist-npapi-plugin.la

libzeitgeist_npapi_plugin_la_SOURCES = \
	plugin/np-zeitgeist.cc \
	$(NULL)

libzeitgeist_npapi_plugin_la_CXXFLAGS = \
	-pedantic -fPIC -Wall -std=c++0x -O2 \
	$(ZEITGEIST_CFLAGS) \
	-I./plugin \
	-I./plugin/third_party \
	-I./plugin/third_party/npapi \
	$(NULL)

libzeitgeist_npapi_plugin_la_LIBADD = \
	$(ZEITGEIST_LIBS) \
	$(NULL)

libzeitgeist_npapi_plugin_la_LDFLAGS = \
	-Wl,--no-undefined \
	-module -avoid-version \
	$(NULL)

# we want to allow also local install
local-install: all
	ln -s $(abs_srcdir)/.libs/libzeitgeist-npapi-plugin.so plugin/libzeitgeist-npapi-plugin.so

local-uninstall: all
