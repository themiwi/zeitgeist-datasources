totemplugindir = $(libdir)/totem/plugins/zg-recent
totemplugin_DATA = zg-recent.totem-plugin zg-recent.ui
totemplugin_LTLIBRARIES = libzg-recent.la

AM_VALAFLAGS = \
	--pkg zeitgeist-1.0 \
	--vapidir=./vapi \
	--pkg bacon-video \
	--pkg totem \
	$(NULL)

libzg_recent_la_SOURCES = \
	totem-zeitgeist-plugin.vala
libzg_recent_la_CFLAGS = \
	-fPIC -Wall -std=c99 \
	$(ZEITGEIST_CFLAGS) \
	$(GTK_CFLAGS) \
	$(TOTEM_PLPARSER_CFLAGS) \
	-I./headers \
	$(NULL)
	
libzg_recent_la_LIBADD = \
	$(ZEITGEIST_LIBS) \
	$(GTK_LIBS) \
	$(NULL)
libzg_recent_la_LDFLAGS = \
	-module -avoid-version \
	$(NULL)


# we want to allow also local install
PLUGIN_FILES = \
	zg-recent.totem-plugin \
	zg-recent.ui \
	./.libs/libzg-recent.so

TOTEM_PLUGIN_HOME_DIR = ~/.local/share/totem/plugins/zg-recent

local-install: all
	mkdir -p $(TOTEM_PLUGIN_HOME_DIR)
	cp $(PLUGIN_FILES) $(TOTEM_PLUGIN_HOME_DIR)

local-uninstall:
	echo Removing $(TOTEM_PLUGIN_HOME_DIR)
	rm -rf $(TOTEM_PLUGIN_HOME_DIR)

