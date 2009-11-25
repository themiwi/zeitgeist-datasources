# -.- coding: utf-8 -.-

# Zeitgeist
#
# Copyright © 2009 Seif Lotfy <seif@lotfy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gedit
import sys
import time

"-------------------------",
print sys.path
"-------------------------",

from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import Event, Subject, Interpretation, Manifestation

try:
	CLIENT = ZeitgeistClient()
except RuntimeError, e:
	print "Unable to connect to Zeitgeist, won't send events. Reason: '%s'" %e
	CLIENT = None

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
		timestamp = time.time()
		print "tab removed", timestamp, doc.get_uri()
		self.docs = self._window.get_documents()

	def TabChangedHandler(self, window, tab):
		doc = tab.get_document()
		if self.docs.count(doc) == 0:
			print "loaded new document ", doc.get_uri()
			doc.connect("saved", self.SaveDocHandler)	
		else:		
			print "tab changed", doc.get_uri()
		self.docs = self._window.get_documents()
		print "***", self.docs

	def SaveDocHandler(self, doc, data):
		print "saved document", doc.get_uri()
		self.docs = self._window.get_documents()
		print "***", self.docs

	def SendToZeitgeist(self, uri, timestamp, event):
		subject = Subject.new_for_values(
			uri=file_obj.get_uri(),
			interpretation=unicode(Interpretation.IMAGE),
			manifestation=unicode(Manifestation.FILE),
			origin=file_obj.get_parent().get_uri(),
			mimetype="", #TBD	
		)
		event = Event.new_for_values(
			timestamp=int(time.time()*1000),
			interpretation=unicode(Interpretation.VISIT_EVENT),
			manifestation=unicode(Manifestation.USER_ACTIVITY),
			actor="application://eog.desktop",
			subjects=[subject,]
		)
		CLIENT.insert_event(event)

class ZeitgeistPlugin(gedit.Plugin):
	def __init__(self):
		gedit.Plugin.__init__(self)
		self._instances = {}

	def activate(self, window):
		print window
		self._instances[window] = ZeitgeistLogic(self, window)

	def deactivate(self, window):
		self._instances[window].deactivate()
		del self._instances[window]


