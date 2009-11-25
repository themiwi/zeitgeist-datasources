import rb
import rhythmdb
import time

from zeitgeist.dbusutils import ZeitgeistClient
from zeitgeist.datamodel import Event, Subject, Interpretation, Manifestation

try:
    CLIENT = ZeitgeistClient()
except RuntimeError, e:
    print "Unable to connect to Zeitgeist, won't send events. Reason: '%s'" %e
    CLIENT = None
    
class ZeitgeistPlugin(rb.Plugin):
    
    def __init__(self):
        rb.Plugin.__init__(self)
        
    def activate(self, shell):
        print "LOADING Zeitgeist plugin ......"
        if CLIENT is not None:
            shell_player = shell.get_player()
            shell_player.connect("playing-changed", self.playing_changed)
            shell_player.connect("playing-source-changed", self.playing_source_changed)
            shell_player.connect("playing-song-changed", self.playing_song_changed)
            self.__current_song = None
        
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
        print ("got playing_changed signal", shell, state)
        
    def playing_source_changed(self, shell, source):
        """ use this signal to trigger changes between local music, radio, online music etc."""
        print ("got playing_source_changed signal", shell, source)
        
    def playing_song_changed(self, shell, entry):
        print ("got playing_song_changed signal", shell, entry)
        db = shell.get_property("db")
        if entry is not None:
            self.__current_song = entry
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
                interpretation=unicode(Interpretation.VISIT_EVENT),
                manifestation=unicode(Manifestation.USER_ACTIVITY),
                actor="application://rhythmbox.desktop",
                subjects=[subject,]
            )
            print event
            CLIENT.insert_event(event)
        
    def deactivate(self, shell):
        print "UNLOADING Zeitgeist plugin ......."
