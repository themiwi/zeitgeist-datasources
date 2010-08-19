
using System;
using System.Collections.Generic;
using Tomboy;
using NDesk.DBus;
using Gtk;
using GLib;
using Mono.Unix.Native;

namespace Tomboy.Zeitgeist
{
	class NoteHandler 
	{
		private static List<string> handled_notes = new List<string>();
		private Note note;
		
		public NoteHandler(Note note) {
			if (handled_notes.Contains(note.Id) == false) {
				this.note = note;
				note.Opened += HandleNoteOpened;
				if (note.HasWindow) {
					HandleNoteOpened();
				}
			}
		}
		
		void HandleNoteOpened (object sender, EventArgs e) {
			HandleNoteOpened();
		}
		void HandleNoteOpened() {
			note.Window.Hidden += HandleNoteWindowHidden;
			note.Window.Shown += HandleNoteWindowShown;
			note.Renamed += HandleNoteRenamed;
			if (note.Window.Visible) {
				HandleNoteWindowShown();	
			}
		}

		void HandleNoteRenamed (Note sender, string old_title)
		{
			Console.WriteLine("Zg: Renamed: " + note.Title);
			ZeitgeistDbus.SendToZeitgeist(note, ZeitgeistDbus.EventInterpretation.ModifyEvent);
		}
		
		void HandleNoteWindowShown (object sender, EventArgs e) {
			HandleNoteWindowShown();
		}
		void HandleNoteWindowShown ()
		{
			Console.WriteLine("Zg: Note window opened: " + note.Title);
			ZeitgeistDbus.SendToZeitgeist(note, ZeitgeistDbus.EventInterpretation.OpenEvent);
		}
		
		void HandleNoteWindowHidden (object sender, EventArgs e)
		{
			Console.WriteLine("Zg: Note window closed: " + note.Title);
			ZeitgeistDbus.SendToZeitgeist(note, ZeitgeistDbus.EventInterpretation.CloseEvent);
		}
	}
	
	class ZeitgeistDbus
	{
		private static ILogger zeitgeist_proxy = 
			Bus.Session.GetObject<ILogger>("org.gnome.zeitgeist.Engine", 
			                               new ObjectPath("/org/gnome/zeitgeist/log/activity"));
		
		public enum EventInterpretation {
			OpenEvent,
			CloseEvent,
			CreateEvent,
			ModifyEvent,
		}
		
		private static string GetEventInterpetation(EventInterpretation e) {
			switch(e) {
			case EventInterpretation.OpenEvent:
				return "http://www.zeitgeist-project.com/ontologies/2010/01/27/zg#AccessEvent";
			case EventInterpretation.CloseEvent:
				return "http://www.zeitgeist-project.com/ontologies/2010/01/27/zg#LeaveEvent";
			case EventInterpretation.CreateEvent:
				return "http://www.zeitgeist-project.com/ontologies/2010/01/27/zg#CreateEvent";
			case EventInterpretation.ModifyEvent:
				return "http://www.zeitgeist-project.com/ontologies/2010/01/27/zg#ModifyEvent";
			default:
				return null;
			}
		}
		
		public static void SendToZeitgeist(Note note, EventInterpretation ev_interp) {
			if (zeitgeist_proxy == null) {
				Console.WriteLine("Zg: cannot connect to zeitgeist, dbus proxy is null");
				return;	
			}
			
			string ev_interp_string = GetEventInterpetation(ev_interp);
			if (ev_interp_string == null) {
				Console.WriteLine("Zg: unknown interpretation type: " + ev_interp.ToString());
				return;
			}
			
			Timeval t;
			Syscall.gettimeofday(out t);
			long millis_now = (t.tv_sec * 1000) + (t.tv_usec / 1000);
			
			Event e = new Event();
			e.metadata = new string[5];
			e.metadata[0] = ""; //id (filled in by Zeitgeist)
			e.metadata[1] = millis_now.ToString();
			e.metadata[2] = ev_interp_string;
			e.metadata[3] = "http://www.zeitgeist-project.com/ontologies/2010/01/27/zg#UserActivity";
			e.metadata[4] = "application://tomboy.desktop";
			
			string[] subject = new string[7];
			subject[0] = note.Uri;
			subject[1] = "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#Document";
			subject[2] = "http://www.semanticdesktop.org/ontologies/nfo#FileDataObject";
			subject[3] = ""; //origin
			subject[4] = "application/x-tomboy"; //mimetype
			subject[5] = note.Title; 
			subject[6] = ""; //storage id
			
			e.subjects = new string[][] { subject };
			e.payload = new byte[0];
			
			GLib.Idle.Add(delegate() {
				SendEvent(e);
				return false;
			});
		}
			
		private static void SendEvent(Event e) {
			int[] inserted;
			try {
				inserted = zeitgeist_proxy.InsertEvents(new Event[] { e });	
			} catch (Exception ex) {
				Console.WriteLine("Zg: insertion failed: " + ex.Message);
				return;
			}
			
			if (inserted.Length > 0) {
				Console.WriteLine("Zg: Inserted event: " + inserted[0]);
			}
			else {
				Console.WriteLine("Zg: Insertion failed");
			}
			return;
		}
	}
	
	[NDesk.DBus.Interface ("org.gnome.zeitgeist.Log")]
	interface ILogger {
		int[] InsertEvents(Event[] events);
	}
		                   
	struct Event {
		public string[] metadata;
		public string[][] subjects;
		public byte[] payload;
	}
	
	public class ZeitgeistAddin : ApplicationAddin
	{
		private bool _init = false;
		public override bool Initialized {
			get { return _init; }
		}
		
		public override
		void Initialize() {
			Console.WriteLine("Zg: init new");
			init_handlers();
			_init = true;
		}
		
		public override
		void Shutdown() {
			Console.WriteLine("Zg: shutdown");
		}
		
		void HandleNoteAdded(object sender, Note new_note) {
			Console.WriteLine("Zg: Note added: " + new_note.Title);
			Console.WriteLine("\t" + new_note.Uri);
			
			new NoteHandler(new_note);
			ZeitgeistDbus.SendToZeitgeist(new_note, ZeitgeistDbus.EventInterpretation.CreateEvent);
		}
		
		public void init_handlers() {
			foreach (Note note in Tomboy.DefaultNoteManager.Notes) {
				new NoteHandler(note);
			}
			
			Tomboy.DefaultNoteManager.NoteAdded -= HandleNoteAdded;
			Tomboy.DefaultNoteManager.NoteAdded += HandleNoteAdded;
		}
	}
	


}
