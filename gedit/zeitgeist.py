import gedit
import sys

class ZeitgeistLogic:
    def __init__(self, plugin, window):
        self._window = window
        self._plugin = plugin
	self.docs = self._window.get_documents()

        self._handler = self._window.connect("tab-removed", self.TabRemovedHandler)
        self._handler = self._window.connect("active-tab-changed", self.TabChangedHandler)
	self._tabs = 0

    def deactivate(self):
        self._window.disconnect(self._handler)
        self._window = None
        self._plugin = None
        self._handler = None

    def TabRemovedHandler(self, window, tab):
	doc = tab.get_document()
	print "tab removed"
	print doc.get_uri()
	print "----------------"
	self.docs = self._window.get_documents()

    def TabChangedHandler(self, window, tab):
	doc = tab.get_document()
	if self.docs.count(doc) == 0:
		print "loaded new document ", doc.get_uri()
		doc.connect("saved", self.SaveDocHandler)	
	else:		
		print "tab changed", doc.get_uri()
	print "----------------" 
	self.docs = self._window.get_documents()

    def SaveDocHandler(self, doc, data):
	print "saved document", doc.get_uri()
	

class ZeitgeistPlugin(gedit.Plugin):
    def __init__(self):
        gedit.Plugin.__init__(self)
        self._instances = {}

    def activate(self, window):
        self._instances[window] = ZeitgeistLogic(self, window)

    def deactivate(self, window):
        self._instances[window].deactivate()
        del self._instances[window]
    
