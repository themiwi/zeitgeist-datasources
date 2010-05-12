GEANY_PLUGIN_DIR = ~/.config/geany/plugins
PLUGIN_FILE = zeitgeist_dataprovider.so

all: clean build

zeitgeist_dataprovider.o:
	gcc -c zeitgeist_dataprovider.c -fPIC `pkg-config --cflags geany zeitgeist-1.0`

zeitgeist_dataprovider.so:
	gcc zeitgeist_dataprovider.o -o zeitgeist_dataprovider.so -shared `pkg-config --libs geany zeitgeist-1.0`

build: zeitgeist_dataprovider.o zeitgeist_dataprovider.so

clean:
	-rm -f *.o
	-rm -f *.so

install: ;

uninstall: ;

local-install:
	mkdir -p $(GEANY_PLUGIN_DIR)
	cp $(PLUGIN_FILE) $(GEANY_PLUGIN_DIR)

local-uninstall:
	-rm -f $(GEANY_PLUGIN_DIR)/$(PLUGIN_FILE)
