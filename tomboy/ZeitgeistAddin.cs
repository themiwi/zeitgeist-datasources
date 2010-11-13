using System;
using Tomboy;
using System.Collections.Generic;
using System.IO;
using Zeitgeist.Datamodel;

namespace Tomboy.Zeitgeist
{
	public class ZeitgeistAddin  : ApplicationAddin
	{
		public ZeitgeistAddin ()
		{
			notesList = new List<NoteHandler>();
		}
		
		#region Overridden methods
		
		public override bool Initialized
		{
			get
			{
				return _init;
			}
		}
		
		public override void Initialize()
		{
			Console.WriteLine("Zg#: init new");
			
			// Initialize the handlers for hooking into Tomboy
			InitHandlers();
			
			_init = true;
		}
		
		public override void Shutdown()
		{
			Console.WriteLine("Zg#: shutdown");
		}
		
		#endregion
		
		public void InitHandlers()
		{
			// For every note present in the store
			
			foreach (Note note in Tomboy.DefaultNoteManager.Notes)
			{
				notesList.Add(new NoteHandler(note));
			}
			
			Tomboy.DefaultNoteManager.NoteAdded -= HandleNoteAdded;
			Tomboy.DefaultNoteManager.NoteAdded += HandleNoteAdded;
			
			Tomboy.DefaultNoteManager.NoteDeleted -= HandleNoteDeleted;
			Tomboy.DefaultNoteManager.NoteDeleted += HandleNoteDeleted;
		}
		
		void HandleNoteAdded(object sender, Note new_note)
		{
			Console.WriteLine("Zg#: Note added: " + new_note.Title);
			Console.WriteLine("\t" + new_note.Uri);
			
			notesList.Add(new NoteHandler(new_note));
			
			ZeitgeistHandler.SendEvent(new_note, Interpretation.Instance.EventInterpretation.CreateEvent);
		}
		
		void HandleNoteDeleted(object sender, Note new_note)
		{
			Console.WriteLine("Zg#: Note deleted: " + new_note.Title);
			Console.WriteLine("\t" + new_note.Uri);
			
			ZeitgeistHandler.SendEvent(new_note, Interpretation.Instance.EventInterpretation.DeleteEvent);
		}
		
		List<NoteHandler> notesList;
		
		private bool _init = false;
		
		#region Public Constants
		
		public const string TomboyUri = "application://tomboy.desktop";
		
		public const string NoteMimetype = "application/x-note";
		
		#endregion
	}
}

