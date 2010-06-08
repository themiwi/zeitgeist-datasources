using RB;

class ZeitgeistRecentPlugin: RB.Plugin {
  private Zeitgeist.Log zg_log;
  private unowned RB.Shell rb_shell;

  public override void activate (RB.Shell shell) {
    zg_log = new Zeitgeist.Log ();
    rb_shell = shell;
  }

  public override void deactivate (RB.Shell shell) {
    rb_shell = null;
  }

}

[ModuleInit]
public GLib.Type register_rb_plugin (GLib.TypeModule module)
{
	return typeof (ZeitgeistRecentPlugin);
}

