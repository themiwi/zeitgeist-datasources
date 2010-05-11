EXTENSION_CONTENT = defaults chrome chrome.manifest install.rdf components/libzeitgeist_xpcom.so components/zeitgeist.xpt

all: clean build

comp:
	$(MAKE) --directory=components

clean:
	$(MAKE) --directory=components clean

build: 
	$(MAKE) comp
	zip -r ../ZeitgeistDataprovider.xpi $(EXTENSION_CONTENT)
	
