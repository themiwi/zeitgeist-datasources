/*
 * ZeitgeistModule.cpp
 * This file is part of zeitgeist dataprovider for firefox 
 *
 * Copyright (C) 2010 - Markus Korn <thekorn@gmx.de>
 * Copyright (C) 2010 - Michal Hruby <michal.mhr@gmail.com>
 * Copyright (C) 2011 - Collabora Ltd.
 *                      By Siegfried-A. Gevatter <siegfried@gevatter.com>
 *
 * zeitgeist dataprovider for firefox is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 3 of the License, or (at your option) any later version.
 * 
 * zeitgeist dataprovider for firefox is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
 
 
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

NS_IMETHODIMP zeitgeistextend::Insert(const char *url,
                                      const char *mimetype,
                                      const nsACString &title_str,
                                      const char *origin)
{
	ZeitgeistEvent		*event;
	gchar				*title = NULL;
	bool				local_file;

	g_debug("zeitgeist start - creating event");

	if (!title_str.IsEmpty ())
	{
		gsize title_len = title_str.EndReading () - title_str.BeginReading ();
		title = g_strndup (title_str.BeginReading (), title_len);
	}

	gchar **uri_parts = g_strsplit(url, "://", 2);
	local_file = g_strcmp0 (uri_parts[0], "file") == 0;
	g_strfreev(uri_parts);

	event = zeitgeist_event_new_full (
			ZEITGEIST_ZG_ACCESS_EVENT,
			ZEITGEIST_ZG_USER_ACTIVITY,
			"application://firefox.desktop",
			zeitgeist_subject_new_full (
				url,
				ZEITGEIST_NFO_WEBSITE,
				(local_file) ? ZEITGEIST_NFO_FILE_DATA_OBJECT : ZEITGEIST_NFO_REMOTE_DATA_OBJECT,
				mimetype,
				origin,
				title,
				"net"),
	NULL);

	if (title) g_free (title);
	g_debug("inserting event");
	zeitgeist_log_insert_events_no_reply(log, event, NULL);
	g_debug("zeitgeist end");

	return NS_OK;
}

