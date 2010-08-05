PLUGIN_FILES = zeitgeist.el

dist_lisp_LISP = $(PLUGIN_FILES)


# we want to allow also local install
EMACS_PLUGIN_HOME_DIR = ~/.emacs/site-lisp

local-install:
	mkdir -p $(EMACS_PLUGIN_HOME_DIR)	
	cp $(PLUGIN_FILES) $(EMACS_PLUGIN_HOME_DIR)
	setenv EMACSLOADPATH $EMACSLOADPATH:$(EMACS_PLUGIN_HOME_DIR)

local-uninstall:
	rm $(EMACS_PLUGIN_HOME_DIR)/$(PLUGIN_FILES)
