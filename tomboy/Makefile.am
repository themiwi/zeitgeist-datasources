CSFLAGS = 		\
	-debug 		\
	-define:DEBUG 	\
	-target:library

ASSEMBLIES = 					\
	$(TOMBOY_ADDINS_LIBS)			\
	$(GTK_SHARP_LIBS)			\
	$(ZEITGEIST_SHARP_LIBS)     \
	-r:Mono.Posix

ADDIN_NAME = ZeitgeistDataprovider
TARGET_DIR = $(top_builddir)/bin/addins
TARGET = $(TARGET_DIR)/$(ADDIN_NAME).dll
CSFILES = \
	$(srcdir)/Zeitgeist.cs     \
	$(srcdir)/ZeitgeistAddin.cs     \
	$(srcdir)/NoteHandler.cs     \
	$(srcdir)/AssemblyInfo.cs
RESOURCES = \
	-resource:$(srcdir)/$(ADDIN_NAME).addin.xml

$(TARGET).mdb: $(TARGET)

$(TARGET): $(CSFILES) $(TOMBOY_EXE_PATH)
	mkdir -p $(TARGET_DIR) && $(GMCS) -out:$@ $(CSFLAGS) $(ASSEMBLIES) $(CSFILES) $(RESOURCES)


addinsdir = $(pkglibdir)/addins
addins_DATA = 			\
	$(TARGET)		\
	$(TARGET).mdb

EXTRA_DIST =            	\
	$(CSFILES) \
	$(srcdir)/$(ADDIN_NAME).addin.xml

CLEANFILES =				\
	$(TARGET).mdb \
	$(TARGET)

