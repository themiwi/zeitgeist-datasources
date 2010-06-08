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

import eog
import gobject
import time

from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import Event, Subject, Interpretation, Manifestation

try:
    CLIENT = ZeitgeistClient()
except RuntimeError, e:
    print "Unable to connect to Zeitgeist, won't send events. Reason: '%s'" %e
    CLIENT = None

class ZeitgeistPlugin(eog.Plugin):

    def __init__(self):
        eog.Plugin.__init__(self)
        self.__current_image = dict()
        self.__run = True
        self.last_image = None
        self.last_origin = None

    def activate(self, window):
        if CLIENT is not None:
            gobject.timeout_add(500, self.get_image, window)
            if CLIENT.get_version() >= [0, 3, 2, 999]:
                CLIENT.register_data_source("9375", "Eye of GNOME", "",
                                            [Event.new_for_values(actor="application://eog.desktop")]
                                            )   
        window.connect("destroy", self.deactivate, window)
    
    def get_image(self, window):
        image = window.get_image()

        if image and image is not self.__current_image.get(window, None):
            self.__current_image[window] = image
            file_obj = image.get_file()
            
            if file_obj.get_uri == self.last_image:
		    subject = Subject.new_for_values(
		        uri=file_obj.get_uri(),
		        interpretation=unicode(Interpretation.IMAGE),
		        manifestation=unicode(Manifestation.FILE_DATA_OBJECT),
		        origin=file_obj.get_parent().get_uri(),
		        text = file_obj.get_uri().split("/")[-1]
		        #~ mimetype="", #TBD                
		    )            
		    event = Event.new_for_values(
		        timestamp=int(time.time()*1000),
		        interpretation=unicode(Interpretation.MODIFY_EVENT),
		        manifestation=unicode(Manifestation.USER_ACTIVITY),
		        actor="application://eog.desktop",
		        subjects=[subject,]
		    )
		    CLIENT.insert_event(event)
	    else:
		if  self.last_image:
			subject = Subject.new_for_values(
				uri= self.last_image,
				interpretation=unicode(Interpretation.IMAGE),
				manifestation=unicode(Manifestation.FILE_DATA_OBJECT),
				origin=file_obj.get_parent().get_uri(),
				text = self.last_image.split("/")[-1]
				#~ mimetype="", #TBD                
			    )            
			event = Event.new_for_values(
				timestamp=int(time.time()*1000),
				interpretation=unicode(Interpretation.LEAVE_EVENT),
				manifestation=unicode(Manifestation.USER_ACTIVITY),
				actor="application://eog.desktop",
				subjects=[subject,]
			    )
			CLIENT.insert_event(event)
		        print "LEAVE", self.last_image
	    subject = Subject.new_for_values(
		uri=file_obj.get_uri(),
		interpretation=unicode(Interpretation.IMAGE),
		manifestation=unicode(Manifestation.FILE_DATA_OBJECT),
		origin=file_obj.get_parent().get_uri(),
		text = file_obj.get_uri().split("/")[-1]
		#~ mimetype="", #TBD                
	    )            
	    event = Event.new_for_values(
		timestamp=int(time.time()*1000),
		interpretation=unicode(Interpretation.ACCESS_EVENT),
		manifestation=unicode(Manifestation.USER_ACTIVITY),
		actor="application://eog.desktop",
		subjects=[subject,]
	    )
	    CLIENT.insert_event(event)
	    self.last_image = file_obj.get_uri()
	    self.last_origin = file_obj.get_parent().get_uri()
	    print "ACCESS", self.last_image

        return self.__run
        
    def deactivate(self, window, *args):
        print "unloading zeitgeist plugin for %r..." %window
        self.__run = False
        try:
            del self.__current_image[window]
        except KeyError:
            pass
