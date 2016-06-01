"zeitgeist.vim - a Zeitgeist logger for Vim
"Author : Jonathan Lambrechts <jonathanlambrechts@gmail.com>
"Installation : drop this file in a vim plugin folder ($HOME/.vim/plugin,/usr/share/vim/vim72/plugin, ...). Vim should be compiled with python enabled.

function! ZeitgeistLog(filename, vim_use_id)
python3 << endpython

import os
import vim
import gi
from gi.repository import Gio, GLib
import time
import dbus
gi.require_version('Zeitgeist', '2.0')
from gi.repository import Zeitgeist

def start():
  try:
    os.zeitgeistclient = Zeitgeist.Log()
    os.got_zeitgeist = True
  except (RuntimeError, ImportError, dbus.exceptions.DBusException):
    os.got_zeitgeist = False
  os.startzg = lambda : None

if not hasattr(os,'startzg'):
  os.startzg = start

os.startzg()


use_id = vim.eval("a:vim_use_id")
filename = vim.eval("a:filename")
precond = os.getuid() != 0 and os.getenv('DBUS_SESSION_BUS_ADDRESS') != None
if os.got_zeitgeist and precond and filename:
  use = {
    "read" : Zeitgeist.ACCESS_EVENT,
    "new" : Zeitgeist.CREATE_EVENT,
    "write" : Zeitgeist.MODIFY_EVENT} [use_id]

  try:
    f = Gio.File.new_for_path(filename)
    fi = f.query_info(Gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE, Gio.FileQueryInfoFlags.NONE)
    uri = f.get_uri()
    mimetype = fi.get_content_type()
  except GLib.Error:
    pass
  else:
    subject = Zeitgeist.Subject(
      uri=str(uri),
      text=str(uri.rpartition("/")[2]),
      interpretation=str(Zeitgeist.DOCUMENT),
      manifestation=str(Zeitgeist.FILE_DATA_OBJECT),
      origin=str(uri.rpartition("/")[0]),
      mimetype=str(mimetype)
    )
    # print("subject: %r" % subject)
    event = Zeitgeist.Event(
      timestamp=int(time.time()*1000),
      interpretation=str(use),
      manifestation=str(Zeitgeist.USER_ACTIVITY),
      actor="application://gvim.desktop"
    )
    event.add_subject(subject)
    # print("event: %r" % event)
    os.zeitgeistclient.insert_event(event)
    # print("insert done")
endpython
endfunction

augroup zeitgeist
au!
au BufRead * call ZeitgeistLog (expand("%:p"), "read")
au BufNewFile * call ZeitgeistLog (expand("%:p"), "new")
au BufWrite * call ZeitgeistLog (expand("%:p"), "write")
augroup END

" vim: sw=2
