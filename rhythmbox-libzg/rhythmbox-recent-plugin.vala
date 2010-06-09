using RB;

struct TimeInfo {
  string name;
  int days;
  TimeInfo (string name, int days)
  {
    this.name = name;
    this.days = days;
  }
}

class ZeitgeistPlaylistSource: RB.StaticPlaylistSource {
  private int days = 1;
  private Zeitgeist.Log zg_log;

  public ZeitgeistPlaylistSource (Zeitgeist.Log zg_log,
                                  RB.Shell shell,
                                  TimeInfo ti,
                                  SourceGroup group,
                                  RhythmDB.EntryType entry_type) {
    GLib.Object (shell: shell,
                 name: ti.name,
                 source_group: group,
                 is_local: false,
                 entry_type: entry_type,
                 query_model: new RhythmDB.QueryModel.empty (shell.db));

    this.days = ti.days;
    this.zg_log = zg_log;
  }

  public void set_up () {
    // FIXME: move to constructor?! it's async anyway...
    load_events ();
  }

  private async void load_events () {
    var t = TimeVal ();
    int64 now = Zeitgeist.timeval_to_timestamp (t);
    t.tv_sec -= 60 * 60 * 24 * this.days;
    int64 start = Zeitgeist.timeval_to_timestamp (t);

    var event = new Zeitgeist.Event ();
    var subject = new Zeitgeist.Subject ();
    subject.set_interpretation (Zeitgeist.NFO_AUDIO);
    event.add_subject (subject);

    var templates = new PtrArray ();
    templates.add (event);

    var events = yield zg_log.find_events (new Zeitgeist.TimeRange (start, now),
                                           (owned) templates,
                                           Zeitgeist.StorageState.ANY, 0,
                                           Zeitgeist.ResultType.MOST_RECENT_EVENTS,
                                           null);

    debug ("Got %u events from zg", events.len);
    for (int i=0; i<events.len; i++) {
      unowned Zeitgeist.Event e = (Zeitgeist.Event*) events.index (i);
      if (e.num_subjects () <= 0) continue;
      var s = e.get_subject (0);

      this.add_to_map (s.get_uri ());
    }
  }
}

class ZeitgeistRecentPlugin: RB.Plugin {
  private Zeitgeist.Log zg_log;
  private unowned RB.Shell rb_shell;

  unowned SourceGroup zg_source_group = null;

  List<TimeInfo?> periods;
  List<unowned RB.Source> sources;

  private void init_source_group () {
    if (zg_source_group != null) return;

    zg_source_group = SourceGroup.register ("zg-recent",
                                            "Zeitgeist",
                                            SourceGroupCategory.FIXED);
  }

  private void append_sources () {
    var db = rb_shell.db;
    unowned RhythmDB.EntryType? entry_type;
    entry_type = RhythmDB.EntryType.get_by_name (db, "song");
    foreach (unowned TimeInfo? ti in periods) {
      var source = new ZeitgeistPlaylistSource (zg_log, rb_shell, ti,
                                                zg_source_group, entry_type);
      rb_shell.append_source (source, null);
      source.set_up ();
      
      this.sources.append (source);
    }
  }

  public override void activate (RB.Shell shell) {
    debug ("plugin activated");
    zg_log = new Zeitgeist.Log ();
    rb_shell = shell;

    sources = new List<unowned RB.Source> ();
    periods = new List<TimeInfo?> ();
    periods.append (TimeInfo ("Today", 1));
    periods.append (TimeInfo ("Yesterday", 2));
    periods.append (TimeInfo ("Last 3 days", 3));
    periods.append (TimeInfo ("Last 7 days", 7));
    periods.append (TimeInfo ("Last 14 days", 14));
    periods.append (TimeInfo ("Last 90 days", 90));

    init_source_group ();
    append_sources ();
  }

  public override void deactivate (RB.Shell shell) {
    foreach (unowned RB.Source src in sources) {
      src.deleted ();
    }
    sources = null;
    rb_shell = null;
    zg_log = null;
    debug ("plugin de-activated");
  }

}

[ModuleInit]
public GLib.Type register_rb_plugin (GLib.TypeModule module)
{
	return typeof (ZeitgeistRecentPlugin);
}

