# compiler and linker
CC = gcc
VALAC = valac

INCS = `pkg-config --libs --cflags zeitgeist-1.0 gtk+-2.0 totem-plparser`
CFLAGS = -g -pedantic -fPIC -Wall -std=c99 -O2 $(INCS) -I./headers

VALASOURCES = totem-zeitgeist-plugin.vala
VALAFLAGS = --pkg zeitgeist-1.0 --vapidir=./vapi --pkg bacon-video --pkg totem

OUTPUT = libtotem-zeitgeist-plugin.so

TOTEM_PLUGIN_DIR = ~/.local/share/totem/plugins
PLUGIN_FILES = zeitgeist.totem-plugin $(OUTPUT)

.SUFFIXES: .c .vala

.vala.c:
	$(VALAC) $(VALAFLAGS) -C $<

# Yes, if we pass -Wl,--no-undefined the build will fail with undefined
#  totem_* functions, apparently these will be present when the extension
#  is run within totem.
$(OUTPUT): $(VALASOURCES:.vala=.c)
	$(CC) -shared -o $@ $(CFLAGS) $<

all: clean build

build: $(OUTPUT)
	@true

clean:
	rm -f $(OUTPUT) $(VALASOURCES:.vala=.c)

local-install: $(PLUGIN_FILES)
	mkdir -p $(TOTEM_PLUGIN_DIR)
	cp $(PLUGIN_FILES) $(TOTEM_PLUGIN_DIR)

local-uninstall:
	for f in $(PLUGIN_FILES); \
	do \
		echo remove $$f; \
		rm -f $(TOTEM_PLUGIN_DIR)/$$f; \
	done

