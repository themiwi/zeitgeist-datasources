totemplugindir = $(libdir)/rhythmbox/plugins/zeitgeist-recent
totemplugin_DATA = zeitgeist-recent.rb-plugin
totemplugin_LTLIBRARIES = libzeitgeist-recent-plugin.la

AM_VALAFLAGS = \
	--pkg zeitgeist-1.0 \
	--vapidir=./vapi \
	--pkg rb \
	--pkg rhythmdb \
	$(NULL)

libzeitgeist_recent_plugin_la_SOURCES = \
	rhythmbox-recent-plugin.vala
libzeitgeist_recent_plugin_la_CFLAGS = \
	-fPIC -Wall -std=c99 \
	$(ZEITGEIST_CFLAGS) \
	$(GTK_CFLAGS) \
	-I./headers \
	$(NULL)
	
libzeitgeist_recent_plugin_la_LIBADD = \
	$(ZEITGEIST_LIBS) \
	$(GTK_LIBS) \
	$(NULL)
libzeitgeist_recent_plugin_la_LDFLAGS = \
	-module -avoid-version \
	$(NULL)


# we want to allow also local install
PLUGIN_FILES = \
	zeitgeist-recent.rb-plugin \
	./.libs/libzeitgeist-recent-plugin.so

TOTEM_PLUGIN_HOME_DIR = ~/.local/share/totem/plugins/zeitgeist-recent

local-install:
	mkdir -p $(TOTEM_PLUGIN_HOME_DIR)
	cp $(PLUGIN_FILES) $(TOTEM_PLUGIN_HOME_DIR)

local-uninstall:
	echo Removing $(TOTEM_PLUGIN_HOME_DIR)
	rm -rf $(TOTEM_PLUGIN_HOME_DIR)

