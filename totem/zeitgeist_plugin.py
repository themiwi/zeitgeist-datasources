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

import totem
import sys
import fnmatch
import time
import gio
import mimetypes

from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import Event, Subject, Interpretation, Manifestation

try:
	CLIENT = ZeitgeistClient()
except RuntimeError, e:
	print "Unable to connect to Zeitgeist, won't send events. Reason: '%s'" %e
	CLIENT = None

class SimpleMatch(object):
	""" Wrapper around fnmatch.fnmatch which allows to define mimetype
	patterns by using shell-style wildcards.
	"""

	def __init__(self, pattern):
		self.__pattern = pattern

	def match(self, text):
		return fnmatch.fnmatch(text, self.__pattern)

	def __repr__(self):
		return "%s(%r)" %(self.__class__.__name__, self.__pattern)

class MimeTypeSet(set):
	""" Set which allows to match against a string or an object with a
	match() method.
	"""

	def __init__(self, *items):
		super(MimeTypeSet, self).__init__()
		self.__pattern = set()
		for item in items:
			if isinstance(item, (str, unicode)):
				self.add(item)
			elif hasattr(item, "match"):
				self.__pattern.add(item)
			else:
				raise ValueError("Bad mimetype '%s'" %item)

	def __contains__(self, mimetype):
		result = super(MimeTypeSet, self).__contains__(mimetype)
		if not result:
			for pattern in self.__pattern:
				if pattern.match(mimetype):
					return True
		return result
		
	def __len__(self):
		return super(MimeTypeSet, self).__len__() + len(self.__pattern)

	def __repr__(self):
		items = ", ".join(sorted(map(repr, self | self.__pattern)))
		return "%s(%s)" %(self.__class__.__name__, items)
		

AUDIO_MIMETYPES = MimeTypeSet(*[SimpleMatch(u"audio/*"),u"application/"])
VIDEO_MIMETYPES = MimeTypeSet(*[SimpleMatch(u"video/*"),u"application/ogg"])

class Zeitgeist(totem.Plugin):
	def __init__ (self):
		totem.Plugin.__init__(self)
		self.totem_object = None
		self.null_metadata = {"year" : "", "tracknumber" : "", "location" : "",
			"title" : "", "album" : "", "time" : "", "genre" : "", "artist" : "",
			 "uri" : "", "mimetype":"", "interpretation":""}
		self.old_metadata = self.null_metadata.copy()
		self.current_uri = None
		self.last_metadata = None
		self.current_metadata = self.null_metadata.copy()
		self.counter = 0

	def activate (self, totem_object):
		self.totem_object = totem_object
		self.totem_object.connect("file-opened", self.handle_opened)
		self.totem_object.connect("file-closed", self.handle_closed)
		self.totem_object.connect("metadata-updated", self.do_update_metadata)

	def deactivate (self, totem):
		self.inform_closed()
		print "deactivate"

	def do_update_metadata(self, totem, artist, title, album, num):
		self.current_metadata = self.null_metadata.copy()
		if title:
			self.current_metadata["title"] = title
		if artist:
			self.current_metadata["artist"] = artist
		if album:
			self.current_metadata["album"] = album
		if self.current_uri:
			self.current_metadata["uri"] = self.current_uri
			################################
			f = gio.File(self.current_uri)
			path = f.get_path()
			info = f.query_info("*")
			mime_type = info.get_content_type()
			###############################
			self.current_metadata["mimetype"] = mime_type
			if mime_type in VIDEO_MIMETYPES:
				self.current_metadata["interpretation"] = Interpretation.VIDEO
			else:
				self.current_metadata["interpretation"] = Interpretation.MUSIC
		self.counter += 1
		if self.counter == 8:
			self.counter = 0
			self.inform_opened()
			self.last_metadata = self.current_metadata

	def handle_opened(self, totem, uri):
		self.current_uri = uri

	def handle_closed(self, totem):
		self.inform_closed()

	def inform_opened(self):
		print "OPENED", self.current_metadata
		self.SendToZeitgeist(self.current_metadata, Interpretation.OPEN_EVENT)

	def inform_closed(self):
		print "CLOSED", self.last_metadata
		if self.last_metadata:
			self.SendToZeitgeist(self.last_metadata, Interpretation.CLOSE_EVENT)

	def SendToZeitgeist(self, doc, event):
		if doc["uri"]:
			subject = Subject.new_for_values(
				uri=doc["uri"],
				text=doc["title"],
				interpretation=unicode(self.current_metadata["interpretation"]),
				manifestation=unicode(Manifestation.FILE),
				origin=doc["uri"].rpartition("/")[0],
				mimetype=doc["mimetype"], #TBD	
			)
			event = Event.new_for_values(
				timestamp=int(time.time()*1000),
				interpretation=unicode(event),
				manifestation=unicode(Manifestation.USER_ACTIVITY),
				actor="application://totem.desktop",
				subjects=[subject,]
			)
			CLIENT.insert_event(event)

