PLUGIN_FILES = zeitgeist.rb-plugin __init__.py

rhythmboxplugindir = $(libdir)/rhythmbox/plugins/zeitgeist-plugin
rhythmboxplugin_DATA = $(PLUGIN_FILES)

# we want to allow also local install
RHYTHMBOX_PLUGIN_HOME_DIR = ~/.local/share/rhythmbox/plugins/zeitgeist-plugin

local-install:
	mkdir -p $(RHYTHMBOX_PLUGIN_HOME_DIR)
	cp $(PLUGIN_FILES) $(RHYTHMBOX_PLUGIN_HOME_DIR)

local-uninstall:
	for f in $(PLUGIN_FILES); \
	do \
		echo remove $$f; \
		rm -f $(RHYTHMBOX_PLUGIN_HOME_DIR)/$$f; \
	done

