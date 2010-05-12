#missing: tomnboy

DATAPROVIDERS = \
	bzr \
	eog \
	epiphany \
	firefox-libzg \
	firefox \
	geany \
	gedit \
	rhythmbox \
	totem


define do-recursive
	for d in $(DATAPROVIDERS);		\
	do								\
		echo '=>' $1 $$d;			\
		$(MAKE) --directory=$$d $1;	\
	done
endef


all: clean build

install: ;

uninstall: ;

local-install:
	@$(call do-recursive,$@)

local-uninstall:
	@$(call do-recursive,$@)

clean:
	@$(call do-recursive,$@)


.PHONY: clean build
build:
	@$(call do-recursive,$@)
