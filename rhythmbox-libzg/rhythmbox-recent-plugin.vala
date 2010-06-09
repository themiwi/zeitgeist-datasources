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

  public ZeitgeistPlaylistSource (RB.Shell shell,
                                  TimeInfo ti,
                                  SourceGroup group,
                                  RhythmDB.EntryType entry_type) {
    GLib.Object (shell: shell,
                 name: ti.name,
                 source_group: group,
                 entry_type: entry_type);

    days = ti.days;
  }

  public void set_up () {
    debug ("set-up called");
  }
}

class ZeitgeistRecentPlugin: RB.Plugin {
  private Zeitgeist.Log zg_log;
  private unowned RB.Shell rb_shell;

  unowned SourceGroup zg_source_group = null;

  List<TimeInfo?> periods;

  private void init_source_group () {
    if (zg_source_group != null) return;

    zg_source_group = SourceGroup.register ("zg-recent",
                                            "Zeitgeist",
                                            SourceGroupCategory.FIXED);
  }

  private void append_sources () {
    foreach (unowned TimeInfo? ti in periods)
    {
      var source = new ZeitgeistPlaylistSource (
        rb_shell, ti, zg_source_group, 
        RhythmDB.Entry.register_type(rb_shell.db, "zgrp"));
      source.set_up ();
      rb_shell.append_source (source, null);
    }
  }

  public override void activate (RB.Shell shell) {
    debug ("plugin activated");
    zg_log = new Zeitgeist.Log ();
    rb_shell = shell;

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

