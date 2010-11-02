totemplugindir = $(libdir)/totem/plugins/zeitgeist
dist_totemplugin_DATA = zeitgeist.totem-plugin
totemplugin_LTLIBRARIES = libtotem-zeitgeist-plugin.la

AM_VALAFLAGS = \
	--pkg zeitgeist-1.0 \
	--vapidir=./vapi \
	--pkg bacon-video \
	--pkg totem \
	$(NULL)

libtotem_zeitgeist_plugin_la_SOURCES = \
	totem-zeitgeist-plugin.vala
libtotem_zeitgeist_plugin_la_CFLAGS = \
	-fPIC -Wall -std=c99 \
	$(ZEITGEIST_CFLAGS) \
	$(GTK_CFLAGS) \
	$(TOTEM_PLPARSER_CFLAGS) \
	-I$(top_srcdir)/totem-libzg/headers \
	$(NULL)
	
libtotem_zeitgeist_plugin_la_LIBADD = \
	$(ZEITGEIST_LIBS) \
	$(GTK_LIBS) \
	$(NULL)
libtotem_zeitgeist_plugin_la_LDFLAGS = \
	-module -avoid-version \
	$(NULL)
	
EXTRA_DIST = \
	$(top_srcdir)/totem-libzg/headers/totem.h \
	$(top_srcdir)/totem-libzg/headers/totem-plugin.h \
	$(top_srcdir)/totem-libzg/headers/totem-playlist.h \
	$(top_srcdir)/totem-libzg/headers/bacon-video-widget.h \
	$(NULL)


# we want to allow also local install
PLUGIN_FILES = zeitgeist.totem-plugin ./.libs/libtotem-zeitgeist-plugin.so

TOTEM_PLUGIN_HOME_DIR = ~/.local/share/totem/plugins/zeitgeist

local-install:
	mkdir -p $(TOTEM_PLUGIN_HOME_DIR)
	cp $(PLUGIN_FILES) $(TOTEM_PLUGIN_HOME_DIR)

local-uninstall:
	echo Removing $(TOTEM_PLUGIN_HOME_DIR)
	rm -rf $(TOTEM_PLUGIN_HOME_DIR)

