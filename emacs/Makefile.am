PLUGIN_FILES  = zeitgeist.el
outfilesemacs = zeitgeist.elc

dist_lisp_LISP = $(PLUGIN_FILES)

# we want to allow also local install
EMACS_PLUGIN_HOME_DIR = ~/.emacs.d/lisp
EMACSLOADPATH=$(EMACS_PLUGIN_HOME_DIR):$$EMACSLOADPATH
emacs_load_text_for_bash = export EMACSLOADPATH=$(EMACS_PLUGIN_HOME_DIR):$$EMACSLOADPATH

local-install:
	mkdir -p $(EMACS_PLUGIN_HOME_DIR)	
	cp $(PLUGIN_FILES)  $(EMACS_PLUGIN_HOME_DIR)
	cp $(outfilesemacs) $(EMACS_PLUGIN_HOME_DIR)
	echo $(emacs_load_text_for_bash) >>~/.profile
	$(emacs_load_text_for_bash)

local-uninstall:
	rm $(EMACS_PLUGIN_HOME_DIR)/$(PLUGIN_FILES)
	rm $(EMACS_PLUGIN_HOME_DIR)/$(outfilesemacs)
