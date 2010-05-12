DATAPROVIDERS = \
	firefox-libzg \
#	firefox


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
	-rm -rf build
	@$(call do-recursive,$@)


.PHONY: clean build
build:
	mkdir build
	@$(call do-recursive,$@)
