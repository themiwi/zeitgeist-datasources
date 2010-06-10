using RB;

struct TimeInfo {
  string name;
  int days;
  TimeInfo (string name, int days) {
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
    int64 start, now;
    var t = TimeVal ();
    now = Zeitgeist.timeval_to_timestamp (t);
    if (this.days > 0)
    {
      t.tv_sec -= 60 * 60 * 24 * this.days;
      start = Zeitgeist.timeval_to_timestamp (t);
    }
    else
    {
      start = 0;
    }

    var event = new Zeitgeist.Event ();
    var subject = new Zeitgeist.Subject ();
    subject.set_interpretation (Zeitgeist.NFO_AUDIO);
    event.add_subject (subject);

    var templates = new PtrArray ();
    templates.add (event);

    var events = 
      yield zg_log.find_events (new Zeitgeist.TimeRange (start, now),
                                (owned) templates,
                                Zeitgeist.StorageState.ANY, 0,
                                Zeitgeist.ResultType.MOST_POPULAR_SUBJECTS,
                                null);

    debug ("Got %u events from zg", events.size ());
    //foreach (unowned Zeitgeist.Event e in events) {
    while (events.has_next ()) {
      unowned Zeitgeist.Event e = events.next ();
      if (e.num_subjects () <= 0) continue;
      var s = e.get_subject (0);

      this.add_to_map (s.get_uri ());
    }
  }
}

class ZeitgeistPopularPlugin: RB.Plugin {
  private Zeitgeist.Log zg_log;
  private unowned RB.Shell rb_shell;

  unowned SourceGroup zg_source_group = null;

  List<TimeInfo?> periods;
  List<unowned RB.Source> sources;

  private void init_source_group () {
    if (zg_source_group != null) return;

    zg_source_group = SourceGroup.register ("zg-popular",
                                            "Most played",
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
    debug ("%s activated", this.get_type ().name ());
    zg_log = new Zeitgeist.Log ();
    rb_shell = shell;

    sources = new List<unowned RB.Source> ();
    periods = new List<TimeInfo?> ();
    periods.append (TimeInfo ("Today", 1));
    periods.append (TimeInfo ("Yesterday", 2));
    periods.append (TimeInfo ("Last week", 7));
    periods.append (TimeInfo ("Last month", 30));
    periods.append (TimeInfo ("Last 3 months", 90));
    periods.append (TimeInfo ("All time", 0));

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
    debug ("%s de-activated", this.get_type ().name ());
  }

}

[ModuleInit]
public GLib.Type register_rb_plugin (GLib.TypeModule module)
{
	return typeof (ZeitgeistPopularPlugin);
}

