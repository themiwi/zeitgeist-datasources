# -.- coding: utf-8 -.-

# Zeitgeist
#
# Copyright © 2009 Markus Korn <thekorn@gmx.de>
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

import rb
import rhythmdb
import time

from zeitgeist.client import ZeitgeistDBusInterface
from zeitgeist.datamodel import Event, Subject, Interpretation, Manifestation

try:
    IFACE = ZeitgeistDBusInterface()
except RuntimeError, e:
    print "Unable to connect to Zeitgeist, won't send events. Reason: '%s'" %e
    IFACE = None
    
class ZeitgeistPlugin(rb.Plugin):
    
    def __init__(self):
        rb.Plugin.__init__(self)
        
    def activate(self, shell):
        print "LOADING Zeitgeist plugin ......"
        if IFACE is not None:
            shell_player = shell.get_player()
            shell_player.connect("playing-changed", self.playing_changed)
            shell_player.connect("playing-source-changed", self.playing_source_changed)
            shell_player.connect("playing-song-changed", self.playing_song_changed)
            self.__current_song = None
            self._shell = shell
        
    @staticmethod
    def get_song_info(db, entry):
        song = {
            "album": db.entry_get(entry, rhythmdb.PROP_ALBUM),
            "artist": db.entry_get(entry, rhythmdb.PROP_ARTIST),
            "title":  db.entry_get(entry, rhythmdb.PROP_TITLE),
            "location": db.entry_get(entry, rhythmdb.PROP_LOCATION),
            "mimetype": db.entry_get(entry, rhythmdb.PROP_MIMETYPE),
        }
        return song
        
        
    def playing_changed(self, shell, state):
        """ using this signal to trigger play/pause switches"""
        pass
        
    def playing_source_changed(self, shell, source):
        """ use this signal to trigger changes between local music, radio, online music etc."""
        pass
        
    def playing_song_changed(self, shell, entry):
        print ("got playing_song_changed signal", shell, entry)
        if self.__current_song is not None:
	    	self.send_to_zeitgeist(self.__current_song, Interpretation.CLOSE_EVENT)

        if entry is not None:
	        self.send_to_zeitgeist(entry, Interpretation.OPEN_EVENT)

        self.__current_song = entry
        
    def send_to_zeitgeist(self, entry, event_type):
        db = self._shell.get_property("db")
        song = self.get_song_info(db, entry)
        subject = Subject.new_for_values(
            uri=song["location"],
            interpretation=unicode(Interpretation.MUSIC),
            manifestation=unicode(Manifestation.FILE),
            #~ origin="", #TBD
            mimetype=song["mimetype"],
            text=" - ".join([song["title"], song["artist"], song["album"]])
        )            
        event = Event.new_for_values(
            timestamp=int(time.time()*1000),
            interpretation=unicode(event_type),
            manifestation=unicode(Manifestation.USER_ACTIVITY),
            actor="application://rhythmbox.desktop",
            subjects=[subject,]
        )
        print event
        IFACE.InsertEvents([event,])
        
    def deactivate(self, shell):
        print "UNLOADING Zeitgeist plugin ......."

