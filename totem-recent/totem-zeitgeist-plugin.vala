using Totem;

class ZeitgeistRecentPlugin: Totem.Plugin {
  private ulong[] signals;

  private Zeitgeist.Log zg_log;
  private unowned Totem.Object totem_object;
  private unowned Gtk.Entry search_box;
  private Totem.VideoList search_video_list;
  private Totem.VideoList related_video_list;

  public override bool activate (Totem.Object totem) throws GLib.Error {
    zg_log = new Zeitgeist.Log ();
    totem_object = totem;

    signals += Signal.connect_swapped (totem, "file-opened",
                                       (Callback) file_opened, this);

    init_ui ();

    return true;
  }

  public override void deactivate (Totem.Object totem) {
    totem_object.remove_sidebar_page ("zeitgeist");
    totem_object = null;

    foreach (ulong id in signals) {
      SignalHandler.disconnect (totem, id);
    }
    signals = null;
  }

  private async void start_search (string search_text_down) {
    var event = new Zeitgeist.Event ();
    // look for audio and video
    var search_subject = new Zeitgeist.Subject ();
    search_subject.set_interpretation (Zeitgeist.NFO_AUDIO);
    event.add_subject (search_subject);
    search_subject = new Zeitgeist.Subject ();
    search_subject.set_interpretation (Zeitgeist.NFO_VIDEO);
    event.add_subject (search_subject);

    var ptr_arr = new PtrArray ();
    ptr_arr.add (event);

    var events = yield zg_log.find_events (new Zeitgeist.TimeRange.to_now (),
                                           (owned) ptr_arr,
                                           Zeitgeist.StorageState.ANY, 1024,
                                           Zeitgeist.ResultType.MOST_RECENT_SUBJECTS,
                                           null);

    int results = 0;

    foreach (var e in events) {
      if (e.num_subjects () <= 0) continue;
      var subject = e.get_subject (0);

      var f = File.new_for_uri (subject.get_uri ());
      var uri_down = f.get_parse_name ().down ();
      var text_down = subject.get_text ().down ();

      if (text_down.str (search_text_down) != null ||
          uri_down.str (search_text_down) != null)
      {
        // matches our search string
        if (f.is_native () && !f.query_exists (null)) continue;

        // valid result
        if (results++ > 64) break;
        var list = search_video_list.get_model () as Gtk.ListStore;
        var iter = Gtk.TreeIter ();
        list.append (out iter);
        list.set (iter,
                  0, null,
                  1, subject.get_text (),
                  2, subject.get_uri (),
                  3, null,
                  -1);

        try
        {
          GLib.Icon icon;
          int icon_size;
          var fi = yield f.query_info_async (FILE_ATTRIBUTE_STANDARD_ICON + "," + FILE_ATTRIBUTE_THUMBNAIL_PATH, 0, Priority.DEFAULT, null);
          if (fi.has_attribute (FILE_ATTRIBUTE_THUMBNAIL_PATH)) {
            var thumb_path = fi.get_attribute_byte_string (FILE_ATTRIBUTE_THUMBNAIL_PATH);
            icon = Icon.new_for_string (thumb_path);
            icon_size = 180;
          }
          else {
            icon = fi.get_icon ();
            icon_size = 48;
          }
          var ii = Gtk.IconTheme.get_default ().lookup_by_gicon (icon, icon_size, 0);
          var pbuf = ii.load_icon ();
          list.set (iter, 0, pbuf, -1);
        }
        catch (GLib.Error err)
        {
          warning ("%s", err.message);
        }
      }
    }
  }

  private void search_started () {
    (search_video_list.get_model () as Gtk.ListStore).clear ();
    var search_text = search_box.get_text ();
    start_search (search_text.down ());
  }

  private void init_ui () {
    var main_window = totem_object.get_main_window ();
    var builder = this.load_interface ("zg-recent.ui", true, main_window);

    Gtk.Widget root = builder.get_object ("zg_vbox") as Gtk.Widget;

    search_box = builder.get_object ("zg_search_entry") as Gtk.Entry;
    search_box.activate.connect (this.search_started);
    var search = builder.get_object ("zg_search_button") as Gtk.Button;
    search.clicked.connect (this.search_started);

    // create treeviews
    Gtk.Container search_scroll = builder.get_object ("zg_scrolled_window_search") as Gtk.Container;
    search_video_list = new Totem.VideoList ();
    var search_list_store = builder.get_object ("zg_list_store_search") as Gtk.TreeModel;
    search_video_list.set_model (search_list_store);
    search_scroll.add (search_video_list);
    set_up_tree_view (search_video_list);

    Gtk.Container related_scroll = builder.get_object ("zg_scrolled_window_related") as Gtk.Container;
    related_video_list = new Totem.VideoList ();
    var related_list_store = builder.get_object ("zg_list_store_related") as Gtk.TreeModel;
    related_video_list.set_model (related_list_store);
    related_scroll.add (related_video_list);
    set_up_tree_view (related_video_list);;

    root.show_all ();

    totem_object.add_sidebar_page ("zeitgeist", "Zeitgeist", root);
  }

  private void set_up_tree_view (Gtk.TreeView view) {
    var renderer = new Totem.CellRendererVideo (true);
    var column = new Gtk.TreeViewColumn.with_attributes ("Video",
                                                         renderer,
                                                         "thumbnail", 0,
                                                         "title", 1,
                                                         null);
    view.append_column (column);
    view.set_headers_visible (false);
    // of course this isn't documented anywhere but without it, it'll crash
    view.set ("mrl-column", 2, "tooltip-column", 1, null);
    view.set ("totem", this.totem_object, null);
  }

  private void file_opened (string mrl, Totem.Object totem) {
  }
}

[ModuleInit]
public GLib.Type register_totem_plugin (GLib.TypeModule module)
{
	return typeof (ZeitgeistRecentPlugin);
}

