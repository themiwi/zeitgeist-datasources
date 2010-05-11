# -.- coding: utf-8 -.-

# Zeitgeist
#
# Copyright © 2009 Markus Korn <thekorn@gmx.de>
# Copyright © 2010 Laszlo Pandy <laszlok2@gmail.com>
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
import gobject
import time

from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import Event, Subject, Interpretation, Manifestation

try:
    IFACE = ZeitgeistClient()
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

            backend_player = shell_player.get_property("player")
            backend_player.connect("eos", self.on_backend_eos)
    
            self.__manual_switch = True
            self.__current_song = None
            self._shell = shell
            
            if IFACE.get_version() >= [0, 3, 2, 999]:
                IFACE.register_data_source("5463", "Rhythmbox", "Play and organize your music collection",
                                            [Event.new_for_values(actor="application://rhythmbox.desktop")]
                                            )
        
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
        
        
    def on_backend_eos(self, backend_player, stream_data, eos_early):
        print "got eos signal"
        # EOS signal means that the song changed because the song is over.
        # ie. the user did not explicitly change the song.
        self.__manual_switch = False
        
    def playing_changed(self, shell, state):
        """ using this signal to trigger play/pause switches"""
        pass
        
    def playing_source_changed(self, shell, source):
        """ use this signal to trigger changes between local music, radio, online music etc."""
        pass
        
    def playing_song_changed(self, shell, entry):
        print ("got playing_song_changed signal", shell, entry)
        if self.__current_song is not None:
            self.send_to_zeitgeist_async(self.__current_song, Interpretation.CLOSE_EVENT)

        if entry is not None:
	        self.send_to_zeitgeist_async(entry, Interpretation.OPEN_EVENT)

        self.__current_song = entry
        gobject.idle_add(self.reset_manual_switch)
        
    def reset_manual_switch(self):
        print "manual_switch reset to True"
        """
        After the eos signal has fired, and after the zeitgeist events have
        been sent asynchronously, reset the manual_switch variable.
        """
        self.__manual_switch = True
        
    def send_to_zeitgeist_async(self, entry, event_type):
        """ 
        We do async here because the "eos" signal is fired
        *after* the "playing-song-changed" signal.
        We don't know if the song change was manual or automatic
        until we get get the eos signal. If the mainloop goes to
        idle, it means there are no more signals scheduled, so we
        will have already received the eos if it was coming.   
        """
        gobject.idle_add(self.send_to_zeitgeist, entry, event_type)
        
    def send_to_zeitgeist(self, entry, event_type):
        db = self._shell.get_property("db")
        song = self.get_song_info(db, entry)
        
        if self.__manual_switch:
            manifest = Manifestation.USER_ACTIVITY
        else:
            manifest = Manifestation.SCHEDULED_ACTIVITY
        
        subject = Subject.new_for_values(
            uri=song["location"],
            interpretation=unicode(Interpretation.AUDIO),
            manifestation=unicode(Manifestation.FILE),
            #~ origin="", #TBD
            mimetype=song["mimetype"],
            text=" - ".join([song["title"], song["artist"], song["album"]])
        )            
        event = Event.new_for_values(
            timestamp=int(time.time()*1000),
            interpretation=unicode(event_type),
            manifestation=unicode(manifest),
            actor="application://rhythmbox.desktop",
            subjects=[subject,]
        )
        print event
        IFACE.insert_event(event)
        
    def deactivate(self, shell):
        print "UNLOADING Zeitgeist plugin ......."

