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
TARGET = $(ADDIN_NAME).dll
CSFILES = \
	$(srcdir)/Zeitgeist.cs     \
	$(srcdir)/ZeitgeistAddin.cs     \
	$(srcdir)/NoteHandler.cs     \
	$(srcdir)/AssemblyInfo.cs
RESOURCES = \
	-resource:$(srcdir)/$(ADDIN_NAME).addin.xml

$(TARGET): $(CSFILES)
	$(GMCS) -out:$@ $(CSFLAGS) $(ASSEMBLIES) $(CSFILES) $(RESOURCES)


addinsdir = $(libdir)/tomboy/addins
addins_DATA = 	$(TARGET)

EXTRA_DIST =            	\
	$(CSFILES) \
	$(srcdir)/$(ADDIN_NAME).addin.xml
	
DISTCLEANFILES = \
	$(TARGET) \
	$(TARGET).mdb
