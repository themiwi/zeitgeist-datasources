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

"""Post-commit hook to submit the commit to Zeitgeist (http://www.zeitgeist-project.com)

Requires bzr 0.15 or higher.

Copyright (C) 2009, Markus Korn <thekorn@gmx.de>
Published under the GNU GPLv2 or later

Installation:
Copy this directory to ~/.bazaar/plugins/zeitgeist/*
"""

import time
import logging
from bzrlib import branch

logging.basicConfig(filename="/dev/null")

install_hook = True
try:
    from zeitgeist import dbusutils
    IFACE = dbusutils.get_engine_interface()
except: # FIXME: adjust this to ImportError, whatever exception is raised
        # as the fix for LP: #397432
    install_hook = False


def post_commit(local, master, old_revno, old_revid, new_revno, new_revid):
    revision = master.repository.get_revision(new_revid)
    if new_revno == 1:
        use = u"CreateEvent"
    else:
        use = u"ModifyEvent"
    item = {
        "timestamp": int(time.time()),
        "uri": unicode(master.base),
        "text": unicode(revision.message),
        "source": "Bzr Branch",
        "content": u"Branch",
        "use": u"http://gnome.org/zeitgeist/schema/1.0/core#%s" %use,
        "mimetype": u"application/x-bzr-branch",
        "tags": u"",
        "icon": u"",
        "app": u"/usr/share/applications/olive-gtk.desktop",
        "origin": u"", 	# we are not sure about the origin of this item,
                        # let's make it NULL, it has to be a string
    }
    items = [dbusutils.plainify_dict(item),]
    IFACE.InsertEvents(items)

if install_hook:
    branch.Branch.hooks.install_named_hook("post_commit", post_commit,
                                           "Zeitgeist dataprovider for bzr")
