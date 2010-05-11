#include "zeitgeist.h"
#include "zeitgeistextend.h"

#include <nsStringAPI.h>
#include <glib.h>
#include <glib-object.h>
#include <zeitgeist.h>


using namespace std;

NS_IMPL_ISUPPORTS1(zeitgeistextend, zeitgeist)

zeitgeistextend::zeitgeistextend()
{
	g_debug("constructor of zeitgeistextend");
	g_type_init ();

	log = (ZeitgeistLog *)g_object_new (ZEITGEIST_TYPE_LOG, NULL);
}

zeitgeistextend::~zeitgeistextend()
{
	g_debug("destructor of zeitgeistextend");
}

NS_IMETHODIMP zeitgeistextend::Insert(const char *url, const nsACString &title)
{
	ZeitgeistEvent		*event;
	gchar             *title_char;

	g_debug("zeitgeist start - creating event");
	
	gsize title_len = title.EndReading () - title.BeginReading ();
	title_char = g_strndup (title.BeginReading (), title_len);

	event = zeitgeist_event_new_full (
			ZEITGEIST_ZG_ACCESS_EVENT,
			ZEITGEIST_ZG_USER_ACTIVITY,
			"app://firefox.desktop",
			zeitgeist_subject_new_full (
				url,
				ZEITGEIST_NFO_WEBSITE,
				ZEITGEIST_NFO_REMOTE_DATA_OBJECT,
				"text/html",
				url,
				title_char,
				"net"),
	NULL);

	g_free (title_char);
	g_debug("inserting event");
	zeitgeist_log_insert_events_no_reply(log, event, NULL);
	g_debug("zeitgeist end");

	return NS_OK;
}

