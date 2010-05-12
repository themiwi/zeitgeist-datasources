GEDIT_PLUGIN_DIR = ~/.gnome2/gedit/plugins
PLUGIN_FILES = zeitgeist.gedit-plugin zeitgeist_plugin.py

all: clean build

build: ;

clean: ;

install: ;

uninstall: ;

local-install:
	mkdir -p $(GEDIT_PLUGIN_DIR)
	cp $(PLUGIN_FILES) $(GEDIT_PLUGIN_DIR)

local-uninstall:
	for f in $(PLUGIN_FILES); \
	do \
		echo remove $$f; \
		rm -f $(GEDIT_PLUGIN_DIR)/$$f; \
	done
