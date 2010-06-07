PLUGIN_FILES = zeitgeist.gedit-plugin zeitgeist_plugin.py

geditplugindir = $(libdir)/gedit-2/plugins
geditplugin_DATA = $(PLUGIN_FILES)

# we want to allow also local install
GEDIT_PLUGIN_HOME_DIR = ~/.gnome2/gedit/plugins

local-install:
	mkdir -p $(GEDIT_PLUGIN_HOME_DIR)
	cp $(PLUGIN_FILES) $(GEDIT_PLUGIN_HOME_DIR)

local-uninstall:
	for f in $(PLUGIN_FILES); \
	do \
		echo remove $$f; \
		rm -f $(GEDIT_PLUGIN_HOME_DIR)/$$f; \
	done

