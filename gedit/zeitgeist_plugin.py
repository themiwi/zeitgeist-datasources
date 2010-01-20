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
		self._window.connect("tab-added", self.TabAddedHandler)
		self._window.connect("tab-removed", self.TabRemovedHandler)
		self._window.connect("active-tab-changed", self.TabChangedHandler)

	def deactivate(self):
		self._window.disconnect_by_func(self.TabAddedHandler)
		self._window.disconnect_by_func(self.TabRemovedHandler)
		self._window.disconnect_by_func(self.TabChangedHandler)
		self._window = None
		self._plugin = None

	def TabAddedHandler(self, window, tab):
		doc = tab.get_document()
		print "Zeitgeist: loaded new tab ", doc.get_uri()
		
		"""
		We don't send an OPEN_EVENT here because that will
		be done after the document's 'loaded' signal is emitted.
		
		We do this because when if there are any empty tabs when
		the user opens a file, the new file will replace the empty 
		tab, and the document's 'loaded' signal will fire, but no
		tab is added and therefore no 'tab-added' is fired.
		"""
		
		doc.connect("saved", self.SaveDocHandler)	
		doc.connect("loaded", self.TabLoadedHandler)

	def TabRemovedHandler(self, window, tab):
		doc = tab.get_document()
		print "Zeitgeist: tab removed", doc.get_uri()
		doc.disconnect_by_func(self.SaveDocHandler)
		doc.disconnect_by_func(self.TabLoadedHandler)
		self.SendToZeitgeist(doc, Interpretation.CLOSE_EVENT)

	def TabChangedHandler(self, window, tab):
		doc = tab.get_document()
		print "Zeitgeist: active tab changed", doc.get_uri()
		self.SendToZeitgeist(doc, Interpretation.FOCUS_EVENT)

	def TabLoadedHandler(self, doc, data):
		print "Zeitgeist: tab loaded document", doc.get_uri()
		self.SendToZeitgeist(doc, Interpretation.OPEN_EVENT)

	def SaveDocHandler(self, doc, data):
		print "Zeitgeist: saved document", doc.get_uri()
		self.SendToZeitgeist(doc, Interpretation.SAVE_EVENT)

	def SendToZeitgeist(self, doc, event):
		if doc.get_uri():
			subject = Subject.new_for_values(
				uri=doc.get_uri(),
				text=doc.get_short_name_for_display (),
				interpretation=unicode(Interpretation.DOCUMENT),
				manifestation=unicode(Manifestation.FILE),
				origin=doc.get_uri().rpartition("/")[0],
				mimetype=doc.get_mime_type(), #TBD	
			)
			event = Event.new_for_values(
				timestamp=int(time.time()*1000),
				interpretation=unicode(event),
				manifestation=unicode(Manifestation.USER_ACTIVITY),
				actor="application://gedit.desktop",
				subjects=[subject,]
			)
			CLIENT.insert_event(event)

class ZeitgeistPlugin(gedit.Plugin):
	def __init__(self):
		gedit.Plugin.__init__(self)
		self._instances = {}

	def activate(self, window):
		self._instances[window] = ZeitgeistLogic(self, window)

	def deactivate(self, window):
		self._instances[window].deactivate()
		del self._instances[window]


