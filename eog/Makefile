EOG_PLUGIN_DIR = ~/.gnome2/eog/plugins
PLUGIN_FILES = zeitgeist.eog-plugin zeitgeist_plugin.py

all: clean build

build: ;

clean: ;

install: ;

uninstall: ;

local-install:
	mkdir -p $(EOG_PLUGIN_DIR)
	cp $(PLUGIN_FILES) $(EOG_PLUGIN_DIR)

local-uninstall:
	for f in $(PLUGIN_FILES); \
	do \
		echo remove $$f; \
		rm -f $(EOG_PLUGIN_DIR)/$$f; \
	done
