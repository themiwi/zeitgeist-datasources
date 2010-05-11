MOZILLA_PLUGIN_FLAGS = $(shell pkg-config --cflags mozilla-plugin)
XUL_SDKDIR = $(shell pkg-config --variable=sdkdir libxul)
XUL_IDLDIR = $(shell pkg-config --variable=idldir libxul)
XPIDL_BIN = $(XUL_SDKDIR)/bin/xpidl
ZG_HEADER = zeitgeist.h
ZG_TYPELIB = zeitgeist.xpt

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

%.o:%.cpp $(ZG_HEADER)
	$(CXX) -fPIC -c -o $@ $(FLAGS) $(INCLUDE) $*.cpp

LIB_SUFFIX=.so
LIBRARY=zeitgeist_xpcom
LIB_FULL=lib$(LIBRARY)$(LIB_SUFFIX)

all: $(ZG_TYPELIB) $(LIB_FULL)

$(ZG_HEADER): zeitgeist.idl
	$(XPIDL_BIN) -m header -I $(XUL_IDLDIR) -o zeitgeist zeitgeist.idl

$(ZG_TYPELIB): zeitgeist.idl
	$(XPIDL_BIN) -m typelib -I $(XUL_IDLDIR) -o zeitgeist zeitgeist.idl

$(LIB_FULL): $(OBJECTS)
	$(CXX) -Wl,--no-undefined -shared -o $(LIB_FULL) $(OBJECTS) $(XUL_LIBS) $(ZG_LIBS)

.PHONY : clean

clean:xpcomclean
xpcomclean:
	-rm -rf $(ZG_HEADER) $(ZG_TYPELIB)
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

