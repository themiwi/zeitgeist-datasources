TOTEM_PLUGIN_DIR = ~/.local/share/totem/plugins
PLUGIN_FILES = zeitgeist.totem-plugin zeitgeist_plugin.py

all: clean build

build: ;

clean: ;

install: ;

uninstall: ;

local-install:
	mkdir -p $(TOTEM_PLUGIN_DIR)
	cp $(PLUGIN_FILES) $(TOTEM_PLUGIN_DIR)

local-uninstall:
	for f in $(PLUGIN_FILES); \
	do \
		echo remove $$f; \
		rm -f $(TOTEM_PLUGIN_DIR)/$$f; \
	done
