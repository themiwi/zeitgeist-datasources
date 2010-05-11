MOZILLA_PLUGIN_FLAGS = $(shell pkg-config --cflags mozilla-plugin)
XUL_SDKDIR = $(shell pkg-config --variable=sdkdir libxul)
XUL_IDLDIR = $(shell pkg-config --variable=idldir libxul)
XPID_BIN = $(XUL_SDKDIR)/bin/xpidl
XPID_TARGET = zeitgeist.h zeitgeist.xpt

#also see: https://developer.mozilla.org/en/XPCOM_Glue
XUL_FLAGS += $(shell pkg-config --cflags libxul)
XUL_LIBS += $(shell pkg-config --libs libxul)

#we also need to link against libzeitgeist-1.0
#this requires ldconfig magic
ZG_FLAGS = $(shell pkg-config --cflags zeitgeist-1.0)
ZG_LIBS = $(shell pkg-config --libs zeitgeist-1.0)

CXX=g++
INCLUDE = \
	$(MOZILLA_PLUGIN_FLAGS) \
	$(ZG_FLAGS) \
	$(XUL_FLAGS) \
	-include "xpcom-config.h"

DEBUG=y
ifeq ($(DEBUG), y)
FLAGS = -g -Wall
else
FLAGS = -O2
endif

OBJECTS = ZeitgeistModule.o  ZeitgeistComponent.o

%.o:%.cpp
	$(CXX) -fPIC -c -o $@ $(FLAGS) $(INCLUDE) $*.cpp

LIB_SUFFIX=.so
LIBRARY=zeitgeist_xpcom
LIB_FULL=lib$(LIBRARY)$(LIB_SUFFIX)

all: xpcomheader $(OBJECTS) $(LIB_FULL)

xpcomheader:
	$(XPID_BIN) -m header -I $(XUL_IDLDIR) -o zeitgeist zeitgeist.idl
	$(XPID_BIN) -m typelib -I $(XUL_IDLDIR) -o zeitgeist zeitgeist.idl

$(LIB_FULL):
	$(CXX) -Wl,--no-undefined -shared -o $(LIB_FULL) $(OBJECTS) $(XUL_LIBS) $(ZG_LIBS)

.PHONY : clean

clean:xpcomclean
xpcomclean:
	-rm -rf $(XPID_TARGET)
	-rm -rf *.o
	-rm -rf *.so

test_ldd:
	# use this target to check the shared object lib
	# if there are unknowwn symbols, see README
	# unknown symbols will FF prevent from starting correctly
	@echo ================;\
	echo checking the .so;\
	echo ================;\
	ldd -r $(LIB_FULL)

