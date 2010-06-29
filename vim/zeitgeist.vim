"zeitgeist.vim - a Zeitgeist logger for Vim
"Author : Jonathan Lambrechts <jonathanlambrechts@gmail.com>
"Installation : drop this file in a vim plugin folder ($HOME/.vim/plugin,/usr/share/vim/vim72/plugin, ...). Vim should be compiled with python enabled.

function! ZeigtgeistLog(filename,use_id)
python << endpython
use = {
	"read" : Interpretation.ACCESS_EVENT,
  "new" : Interpretation.CREATE_EVENT,
  "write" : Interpretation.MODIFY_EVENT} [vim.eval("a:use_id")]

uri = "file://" + vim.eval("a:filename")
fi = gio.File(uri).query_info(gio.FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE)
mimetype = fi.get_content_type()
subject = Subject.new_for_values(
  uri=unicode(uri),
  text=unicode(uri.rpartition("/")[2]),
  interpretation=unicode(Interpretation.DOCUMENT),
  manifestation=unicode(Manifestation.FILE_DATA_OBJECT),
  origin=unicode(uri.rpartition("/")[0]),
  mimetype=unicode(mimetype)
)
event = Event.new_for_values(
  timestamp=int(time.time()*1000),
  interpretation=unicode(use),
  manifestation=unicode(Manifestation.USER_ACTIVITY),
  actor="application://gvim.desktop",
  subjects=[subject,]
)
zeitgeistclient.insert_event(event)
endpython
endfunction

python << endpython
import time
import gio
import vim
from zeitgeist.client import ZeitgeistClient
from zeitgeist.datamodel import Subject, Event, Interpretation, Manifestation
  
try:
  zeitgeistclient = ZeitgeistClient()
except RuntimeError, e:
  zeitgeistclient = None
endpython
augroup zeitgeist
au!
au BufRead * call ZeigtgeistLog (expand("%:p"), "read")
au BufNewFile * call ZeigtgeistLog (expand("%:p"), "new")
au BufWrite * call ZeigtgeistLog (expand("%:p"), "write")
augroup END
