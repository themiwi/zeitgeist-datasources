# compiler and linker
CC = g++

# Customize below to fit your system

INCS = `pkg-config --libs --cflags zeitgeist-1.0` -I./third_party -I./third_party/npapi -I./
#INCS = `pkg-config --libs --cflags libxul nspr zeitgeist-1.0`
CPPFLAGS = -DXULRUNNER_SDK
CFLAGS = -g -pedantic -fPIC -Wall -std=c++0x -O2 ${INCS}

OUTPUT = libzeitgeist-npapi-plugin.so

all: $(OUTPUT)

$(OUTPUT): np-zeitgeist.c
	$(CC) -Wl,--no-undefined -shared -o $@ $(CFLAGS) $<

clean:
	rm -f $(OUTPUT)
