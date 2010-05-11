GECKO_SDK_PATH = /usr/include/xulrunner-1.9.2.3
XPID_BIN = /usr/lib/xulrunner-1.9.2.3/xpidl
XPID_TARGET = zeitgeist.h zeitgeist.xpt

#also see: https://developer.mozilla.org/en/XPCOM_Glue
XUL_FLAGS += $(shell pkg-config --cflags --libs /usr/lib/pkgconfig/libxul.pc)
#we also need to link against libzeitgeist-1.0
#this requires ldconfig magic
XUL_FLAGS += -lzeitgeist-1.0

ZG_FLAGS = $(shell pkg-config --cflags --libs /usr/lib/pkgconfig/glib-2.0.pc /usr/lib/pkgconfig/gobject-2.0.pc)
ZG_FLAGS += -I/usr/local/include/zeitgeist-1.0

CXX=g++
INCLUDE = -I $(GECKO_SDK_PATH) -include "xpcom-config.h" -I /usr/include/nspr

DEBUG=y
ifeq ($(DEBUG), y)
FLAGS = -g -Wall
else
FLAGS = -O2
endif

OBJECTS = ZeitgeistModule.o  ZeitgeistComponent.o

%.o:%.cpp
	$(CXX) -fPIC -c -o $@ $(FLAGS) $(INCLUDE) $(ZG_FLAGS) $*.cpp

LIB_SUFFIX=.so
LIBRARY=zeitgeist_xpcom
LIB_FULL=lib$(LIBRARY)$(LIB_SUFFIX)

all: xpcomheader $(OBJECTS) $(LIB_FULL)

xpcomheader:
	$(XPID_BIN) -m header -I /usr/share/idl/xulrunner-1.9.2.3 -o zeitgeist zeitgeist.idl
	$(XPID_BIN) -m typelib -I /usr/share/idl/xulrunner-1.9.2.3 -o zeitgeist zeitgeist.idl

$(LIB_FULL):
	$(CXX) -shared -o $(LIB_FULL) $(OBJECTS) $(XUL_FLAGS)

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

