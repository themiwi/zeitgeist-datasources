bzrplugindir = $(datadir)/pyshared/bzrlib/plugins/zeitgeist
bzrplugin_DATA = __init__.py

# we want to allow also local install
BZR_PLUGIN_HOME_DIR = ~/.bazaar/plugins/zeitgeist

local-install:
	mkdir -p $(BZR_PLUGIN_HOME_DIR)
	cp __init__.py $(BZR_PLUGIN_HOME_DIR)

local-uninstall:
	-rm -rf $(BZR_PLUGIN_HOME_DIR)

