RB_PLUGIN_DIR = ~/.local/share/rhythmbox/plugins
ZG_PLUGIN_DIR = $(RB_PLUGIN_DIR)/zeitgeist_plugin
PLUGIN_FILE = zeitgeist.rb-plugin

all: clean build

build: ;

clean: ;

install: ;

uninstall: ;

local-install:
	mkdir -p $(ZG_PLUGIN_DIR)
	cp $(PLUGIN_FILE) $(RB_PLUGIN_DIR)
	cp __init__.py $(ZG_PLUGIN_DIR)

local-uninstall:
	-rm -rf $(ZG_PLUGIN_DIR)
	-rm -rf $(RB_PLUGIN_DIR)/$(PLUGIN_FILE)
