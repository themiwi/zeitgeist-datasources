SUBDIRS = $(PLUGINS)

local-install:
	for d in $(PLUGINS); \
	do \
		$(MAKE) --directory=$$d $@; \
	done

local-uninstall:
	for d in $(PLUGINS); \
	do \
		$(MAKE) --directory=$$d $@; \
	done

