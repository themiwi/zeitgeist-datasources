using Totem;

struct MediaInfo {
  int64 timestamp;
  bool sent_access;
  string? mrl;
  string? mimetype;
  string? title;
  string? interpretation;
  string? artist;
  string? album;
}

class ZeitgeistPlugin: Totem.Plugin {
  private MediaInfo current_media;
  // timer waiting while we get some info about current playing media
  private uint media_info_timeout;
  // timer making sure we don't wait indefinitely
  private uint timeout_id;
  private ulong[] signals;

  private Zeitgeist.Log zg_log;
  private unowned Totem.Object totem_object;

  public override bool activate (Totem.Object totem) throws GLib.Error {
    zg_log = new Zeitgeist.Log ();
    totem_object = totem;
    current_media = MediaInfo ();

    signals += Signal.connect_swapped (totem, "file-opened",
                                       (Callback) file_opened, this);
    signals += Signal.connect_swapped (totem, "file-closed",
                                       (Callback)file_closed, this);
    signals += Signal.connect_swapped (totem, "metadata-updated",
                                       (Callback) metadata_changed, this);
    signals += Signal.connect_swapped (totem, "notify::playing",
                                       (Callback) playing_changed, this);
    return true;
  }

  public override void deactivate (Totem.Object totem) {
    // we don't always get file-closed, so lets simulate it
    file_closed (totem);

    totem_object = null;

    foreach (ulong id in signals) {
      SignalHandler.disconnect (totem, id);
    }
    signals = null;

    // cleanup timers
    if (media_info_timeout != 0) Source.remove (media_info_timeout);
    if (timeout_id != 0) Source.remove (timeout_id);

    media_info_timeout = 0;
    timeout_id = 0;
  }

  private void restart_watcher (uint interval) {
    if (timeout_id != 0) {
      Source.remove (timeout_id);
    }
    timeout_id = Timeout.add (interval, timeout_cb);
  }

  private void file_opened (string mrl, Totem.Object totem) {
    if (current_media.mrl != null) {
      // we don't always get file-closed, so lets simulate it
      file_closed (totem);
    }

    current_media = MediaInfo ();
    current_media.mrl = mrl;

    TimeVal cur_time = TimeVal ();
    current_media.timestamp = Zeitgeist.timeval_to_timestamp (cur_time);

    // wait a bit for the media info
    if (media_info_timeout == 0) {
      media_info_timeout = Timeout.add (250, wait_for_media_info);
      // but make sure we dont wait indefinitely
      restart_watcher (15000);
    } else {
      warning ("already had timeout!");
    }
  }

  private void file_closed (Totem.Object totem) {
    if (current_media.sent_access && current_media.mrl != null) {
      // send close event
      TimeVal cur_time = TimeVal ();
      current_media.timestamp = Zeitgeist.timeval_to_timestamp (cur_time);
      send_event_to_zg (true);

      current_media.mrl = null;
    }

    // kill timers
    if (media_info_timeout != 0) Source.remove (media_info_timeout);
    media_info_timeout = 0;
    if (timeout_id != 0) Source.remove (timeout_id);
    timeout_id = 0;
  }

  private void metadata_changed (string? artist, string? title, string? album,
                                 uint track_num, Totem.Object totem) {
    // we can get some notification after sending event to ZG, so ignore it
    if (media_info_timeout != 0) {
      current_media.artist = artist;
      current_media.title = title;
      current_media.album = album;
    }
  }

  private bool timeout_cb () {
    if (media_info_timeout != 0) {
      // we don't have any info besides the url, so use the short_title

      Source.remove (media_info_timeout);
      media_info_timeout = 0;

      current_media.title = totem_object.get_short_title ();
      timeout_id = 0;
      wait_for_media_info ();
    }

    timeout_id = 0;
    return false;
  }

  private bool wait_for_media_info () {
    if (current_media.title != null && totem_object.is_playing ()) {
      Value val;
      var video = totem_object.get_video_widget () as Bacon.VideoWidget;
      video.get_metadata (Bacon.MetadataType.HAS_VIDEO, out val);
      current_media.interpretation = val.get_boolean () ?
        Zeitgeist.NFO_VIDEO : Zeitgeist.NFO_AUDIO;

      var f = File.new_for_uri (current_media.mrl);
      if (f.query_exists (null)) {
        try {
          var fi = f.query_info (FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE, 0, null);
          current_media.mimetype = fi.get_content_type ();
        } catch (GLib.Error err) {
          warning ("%s", err.message);
        }
      }
      
      // send event
      send_event_to_zg ();
      current_media.sent_access = true;

      // cleanup timers
      if (timeout_id != 0) Source.remove (timeout_id);
      timeout_id = 0;
      media_info_timeout = 0;
      return false;
    }
    // wait longer
    return true;
  }

  private void playing_changed () {
    if (media_info_timeout == 0 && current_media.sent_access == false) {
      wait_for_media_info ();
    }

    // end of playlist
    if (!totem_object.is_playing () && current_media.sent_access) {
      // FIXME: sends leave event even if the user just pauses 
      // the playback for a little while
      file_closed (totem_object);
    }
  }

  private void send_event_to_zg (bool leave_event = false) {
    if (current_media.mrl != null && current_media.title != null) {
      string event_interpretation = leave_event ?
        Zeitgeist.ZG_LEAVE_EVENT : Zeitgeist.ZG_ACCESS_EVENT;
      /*
      debug ("About to send %s event to ZG for: %s [%s] (%s)",
             leave_event ? "LEAVE" : "ACCESS",
             current_media.mrl,
             current_media.title,
             current_media.mimetype);
      */
      string origin = "";
      unowned string substr = current_media.mrl.rchr (-1, '/');
      if (substr != null) {
        size_t n = (char*)substr - (char*)current_media.mrl;
        origin = current_media.mrl.ndup (n);
      }
      var subject = new Zeitgeist.Subject.full (current_media.mrl,
                                                current_media.interpretation,
                                                Zeitgeist.NFO_FILE_DATA_OBJECT,
                                                current_media.mimetype,
                                                origin,
                                                current_media.title,
                                                "");
      var event = new Zeitgeist.Event.full (event_interpretation,
                                            Zeitgeist.ZG_USER_ACTIVITY,
                                            "application://totem.desktop",
                                            subject, null);
      event.set_timestamp (current_media.timestamp);
      zg_log.insert_events_no_reply (event, null);
    }
  }
}

[ModuleInit]
public GLib.Type register_totem_plugin (GLib.TypeModule module)
{
	return typeof (ZeitgeistPlugin);
}

