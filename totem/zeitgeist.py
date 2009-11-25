import totem

class Zeitgeist(totem.Plugin):
	def __init__ (self):
		totem.Plugin.__init__(self)
		self.totem_object = None
		self.null_metadata = {"year" : "", "tracknumber" : "", "location" : "",
			"title" : "", "album" : "", "time" : "", "genre" : "", "artist" : "", "uri" : ""}
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
		print "OPENED"
		print self.current_metadata
		print "--------------------"

	def inform_closed(self):
		print "CLOSED"
		print self.last_metadata
		print "--------------------"

