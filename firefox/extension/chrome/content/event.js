var ZeitgeistProgressListener = {
	onStateChange: function(aBrowser, aProgress, aRequest, aStateFlags) {
		
		//Don't do anything if Private Browsing is enabled
		var pbs = Components.classes["@mozilla.org/privatebrowsing;1"]
				.getService(Components.interfaces.nsIPrivateBrowsingService);
		if (pbs.privateBrowsingEnabled) return;   
						
		if (aStateFlags & Components.interfaces.nsIWebProgressListener.STATE_STOP) {
			let uri = aBrowser.currentURI.spec;
			//Ignore pages without titles (generally redirect pages)
			if (aBrowser.contentTitle == "") return;
			
			let mimetype = aBrowser.contentDocument.contentType;
			if (aRequest.name == uri && !this.ignore_uri(uri)) {
				var origin;
				var parts = uri.split("://", 2);
				if (parts[0] == "file") {
					// Local file URI, we just trim it to directory in which the file is
					origin = uri.substring(0, uri.lastIndexOf('/') + 1);
				} else {
					// HTTP(S), FTP or any other URI, we only take up to the domain name
					origin = parts[0] + "://" + parts[1].split("/")[0] + "/";
				}
						
				let subject = libzeitgeist.zeitgeist_subject_new_full( 	uri,
																	"http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#Website",
																	"http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#RemoteDataObject",
																	mimetype,
																	origin,
																	aBrowser.contentTitle,
																	"net");
				
				let event = libzeitgeist.zeitgeist_event_new_full(  "http://www.zeitgeist-project.com/ontologies/2010/01/27/zg#AccessEvent", 
																	"http://www.zeitgeist-project.com/ontologies/2010/01/27/zg#UserActivity", 
																	"application://firefox.desktop",
																	subject,
																	null);
								
				libzeitgeist.zeitgeist_log_insert_events_no_reply(libzeitgeist.log, event, null);
				
				//Log event in Firefox's error console if logging pref is true
				var prefs = Components.classes["@mozilla.org/preferences-service;1"]
										.getService(Components.interfaces.nsIPrefBranch);
				if (prefs.getBoolPref("extensions.zeitgeist.log")) {
					zeitgeist.debug("Event added to zeitgeist:" +
									"\n\t\tevent interpretation: EVENT_INTERPRETATION.ACCESS_EVENT" +
									"\n\t\tEvent manifestation: EVENT_MANIFESTATION.USER_ACTIVITY" +
									"\n\t\tActor: application://firefox.desktop" +
									"\n\t\tSubject:\n\t\t\tSubject interpretation: WEBSITE" +
									"\n\t\t\tSubject manifestation: FILE_DATA_OBJECT.REMOTE_DATA_OBJECT" +
									"\n\t\t\turl: " + uri +
									"\n\t\t\tmimetype: "+ mimetype + 
									"\n\t\t\torigin: " + origin + 
									"\n\t\t\ttitle: " + aBrowser.contentTitle +
									"\n\t\t\tstorage: net");
				}
				
				var googlemail_view_regex = new RegExp("mail\\.google\\.com");
				if (ZeitgeistPrefObserver.get_bool("enable_googlemail") & googlemail_view_regex.test(uri)) {
					var dmt = aBrowser.contentDocument;
					var head = dmt.getElementsByTagName("title")[0];
					head.addEventListener("DOMSubtreeModified", function(event){
						if (dmt.title) {
							let subject = libzeitgeist.zeitgeist_subject_new_full( 	dmt.location.href,
															"http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#Website",
															"http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#RemoteDataObject",
															dmt.contentType,
															"http://mail.google.com/",
															dmt.title,
															"net");
							let event = libzeitgeist.zeitgeist_event_new_full(  "http://www.zeitgeist-project.com/ontologies/2010/01/27/zg#AccessEvent", 
															"http://www.zeitgeist-project.com/ontologies/2010/01/27/zg#UserActivity", 
															"application://firefox.desktop",
															subject,
															null);
							
							libzeitgeist.zeitgeist_log_insert_events_no_reply(libzeitgeist.log, event, null);
						};
					}, false);
				}
			}
		}
	},
	
	// we don't implement this methods
	onStatusChange: function(){},
	onLocationChange: function(){},
	onSecurityChange: function(){},
	onProgressChange: function(){},
	
	//Useful helpers	
	ignore_uri: function(uri) {
		for (pattern in ZeitgeistPrefObserver.ignored_uris) {
			if (ZeitgeistPrefObserver.ignored_uris[pattern].test(uri)) {
				return true;
			}
		}
		return false;
	},
};

var zeitgeist = {
	init: function() { 
		ZeitgeistPrefObserver.register();
		gBrowser.addTabsProgressListener(ZeitgeistProgressListener);
		libzeitgeist.init();
	},
	
	uninit: function() {
		ZeitgeistPrefObserver.unregister();
		gBrowser.removeTabsProgressListener(ZeitgeistProgressListener);
		libzeitgeist.shutdown();
	},
	
	debug: function (aMessage) {
		var consoleService = Components.classes["@mozilla.org/consoleservice;1"]
			.getService(Components.interfaces.nsIConsoleService);
		consoleService.logStringMessage("Zeitgeist Extension (" + new Date() + " ):\n\t" + aMessage);
		window.dump("Zeitgeist Extension: (" + new Date() + " ):\n\t" + aMessage + "\n");
	}
};

var ZeitgeistPrefObserver = {
	register: function() {
		// First we'll need the preference services to look for preferences.
		var prefService = Components.classes["@mozilla.org/preferences-service;1"]
			.getService(Components.interfaces.nsIPrefService);
			
		// For this._branch we ask that the preferences for extensions.myextension. and children
		this._branch = prefService.getBranch("extensions.zeitgeist.");

		// Now we queue the interface called nsIPrefBranch2. This interface is described as:  
		// "nsIPrefBranch2 allows clients to observe changes to pref values."
		this._branch.QueryInterface(Components.interfaces.nsIPrefBranch2);
		
		// Finally add the observer.
		this._branch.addObserver("", this, false);
	},

	unregister: function() {
		if(!this._branch) return;
		this._branch.removeObserver("", this);
	},

	observe: function(aSubject, aTopic, aData) {
		if(aTopic != "nsPref:changed") return;
			// aSubject is the nsIPrefBranch we're observing (after appropriate QI)
			// aData is the name of the pref that's been changed (relative to aSubject)
			switch (aData) {
				case "ignored_uris":
					// extensions.zeitgeist.ignored_uris was changed
					pattern = this.get_string(aData);
					this.ignored_uris = this.make_pattern(pattern);
					break;
				case "enable_googlemail":
					// extensions.zeitgeist.enable_googlemail was changed
					enable_googlemail = this.get_bool(aData);
					break;
				case "log":
					break;
			}
	},
		
	make_pattern: function(pattern) {
		for (item in pattern) {
			pattern[item] = new RegExp(pattern[item]);
		}
		return pattern;
	},

	get_string: function(key) {
		try {
			return JSON.parse(this._branch.getCharPref(key));
		} catch(err) {
		}
	},

	get_bool: function(key) {
		try {
			return this._branch.getBoolPref(key);
		} catch(err) {
		}
	}
};

window.addEventListener("load", function() {zeitgeist.init()}, false);
window.addEventListener("unload", function() {zeitgeist.uninit()}, false);
