PLUGIN_FILES = zeitgeist.eog-plugin zeitgeist_plugin.py

eogplugindir = $(libdir)/eog/plugins
eogplugin_DATA = $(PLUGIN_FILES)

# we want to allow also local install
EOG_PLUGIN_HOME_DIR = ~/.gnome2/eog/plugins

local-install:
	mkdir -p $(EOG_PLUGIN_HOME_DIR)
	cp $(PLUGIN_FILES) $(EOG_PLUGIN_HOME_DIR)

local-uninstall:
	for f in $(PLUGIN_FILES); \
	do \
		echo remove $$f; \
		rm -f $(EOG_PLUGIN_HOME_DIR)/$$f; \
	done

