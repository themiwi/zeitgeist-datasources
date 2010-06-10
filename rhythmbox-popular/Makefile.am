rhythmboxplugindir = $(libdir)/rhythmbox/plugins/zeitgeist-popular
rhythmboxplugin_DATA = zeitgeist-popular.rb-plugin
rhythmboxplugin_LTLIBRARIES = libzeitgeist-popular-plugin.la

AM_VALAFLAGS = \
	--pkg zeitgeist-1.0 \
	--vapidir=./vapi \
	--pkg rb \
	--pkg rhythmdb \
	$(NULL)

libzeitgeist_popular_plugin_la_SOURCES = \
	rhythmbox-popular-plugin.vala
libzeitgeist_popular_plugin_la_CFLAGS = \
	-fPIC -Wall -std=c99 \
	$(ZEITGEIST_CFLAGS) \
	$(GTK_CFLAGS) \
	$(LIBXML_CFLAGS) \
	-I./headers \
	-I./headers/shell \
	$(NULL)
	
libzeitgeist_popular_plugin_la_LIBADD = \
	$(ZEITGEIST_LIBS) \
	$(GTK_LIBS) \
	$(NULL)
libzeitgeist_popular_plugin_la_LDFLAGS = \
	-module -avoid-version \
	$(NULL)


# we want to allow also local install
PLUGIN_FILES = \
	zeitgeist-popular.rb-plugin \
	./.libs/libzeitgeist-popular-plugin.so

RB_PLUGIN_HOME_DIR = ~/.local/share/rhythmbox/plugins/zeitgeist-popular

local-install: all
	mkdir -p $(RB_PLUGIN_HOME_DIR)
	cp $(PLUGIN_FILES) $(RB_PLUGIN_HOME_DIR)

local-uninstall:
	echo Removing $(RB_PLUGIN_HOME_DIR)
	rm -rf $(RB_PLUGIN_HOME_DIR)

