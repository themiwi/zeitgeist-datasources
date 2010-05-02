//      This program is free software; you can redistribute it and/or modify
//      it under the terms of the GNU General Public License as published by
//      the Free Software Foundation; either version 2 of the License, or
//      (at your option) any later version.
//      
//      This program is distributed in the hope that it will be useful,
//      but WITHOUT ANY WARRANTY; without even the implied warranty of
//      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//      GNU General Public License for more details.
//      
//      You should have received a copy of the GNU General Public License
//      along with this program; if not, write to the Free Software
//      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
//      MA 02110-1301, USA.
//
//      Copyright 2009 Markus Korn <thekorn@gmx.de>

window.addEventListener("load", function() { ZeitgeistExtension.init(); }, false);

function debug(aMessage) {
    var consoleService = Components.classes["@mozilla.org/consoleservice;1"]
        .getService(Components.interfaces.nsIConsoleService);
    consoleService.logStringMessage("Zeitgeist Extension: " + aMessage);
}

function log_console(aMessage) {
    window.dump(aMessage + "\n");
}

function getTraceback(fileobj) {
    var fileStream = Components.classes[
        "@mozilla.org/network/file-input-stream;1"
    ].createInstance(Components.interfaces.nsIFileInputStream);
    debug("try to get a Traceback");
    fileStream.init(fileobj, -1, 0, 0);
    
    var charset = "UTF-8";
    const replacementChar = Components.interfaces.nsIConverterInputStream.DEFAULT_REPLACEMENT_CHARACTER;
    var is = Components.classes["@mozilla.org/intl/converter-input-stream;1"]
                   .createInstance(Components.interfaces.nsIConverterInputStream);
    is.init(fileStream, charset, 1024, replacementChar);
    var str = {};
    var traceback = "";
    while (is.readString(4096, str) != 0) {
        traceback += str.value;
    }

    is.close();
    fileStream.close();
    return traceback;    
}

var ZeitgeistExtension = {
    init: function() {
        debug("init zeitgeist extension");
        var appcontent = document.getElementById("appcontent");   // browser
        if(appcontent) {
            ZeitgeistExtension.loadPastEvents();
        }
    },
    
    loadPastEvents: function() {
        //~ 1.) create tempfile
        //~ 2.) get last event to this file
        //~ 3.) read last event from this file
        //~ 4.) query history after last event
        
        
        // find OS temp dir to put the tempfile in
        // https://developer.mozilla.org/index.php?title=File_I%2F%2FO#Getting_special_files
        var tmpdir = Components.classes["@mozilla.org/file/directory_service;1"]
                     .getService(Components.interfaces.nsIProperties)
                     .get("TmpD", Components.interfaces.nsIFile);
        // create a randomly named tempfile in the tempdir
        var tmpfile = Components.classes["@mozilla.org/file/local;1"]
                     .createInstance(Components.interfaces.nsILocalFile);
        tmpfile.initWithPath(
            tmpdir.path + "/zeitgeist.firefox.history." + Math.random()
        );
        tmpfile.createUnique(tmpfile.NORMAL_FILE_TYPE, 0600);
        
        ZeitgeistExtension.runScript(["--last", "--iofile", tmpfile.path],
            function(p, finishState, unused_data) {
                var err_code = p.QueryInterface(
                    Components.interfaces.nsIProcess
                ).exitValue;
                switch (err_code) {
                    case 0:
                        ZeitgeistExtension.readLastEvent(tmpfile);
                        break;
                    case 100:
                        Components.utils.reportError(
                            "Zeitgeist daemon is not running and can not be launched"
                        );
                        break;
                    default:
                        traceback = getTraceback(tmpfile);
                        Components.utils.reportError(
                            "Unknown Zeitgeist Error"+err_code+"\nTraceback\n"+traceback
                        );
                        break;
                }
            }
        );
    },
    
    readLastEvent: function(tmpfile) {        
        var fileStream = Components.classes[
            "@mozilla.org/network/file-input-stream;1"
        ].createInstance(Components.interfaces.nsIFileInputStream);
        debug("getting last inserted event from zeitgeist");
        fileStream.init(tmpfile, -1, 0, 0);        
        fileStream.QueryInterface(Components.interfaces.nsILineInputStream);

        var line = {};
        fileStream.readLine(line);
        if (null != line.value) {
           var timestamp = line.value;
        }
        fileStream.close();
        debug("last insert at "+timestamp);
        ZeitgeistExtension.loadHistory(timestamp, tmpfile);
    },
    
    loadHistory: function(timestamp, tmpfile) {
        debug("querying history beginning at "+timestamp);
        var historyService = Components.classes[
            "@mozilla.org/browser/nav-history-service;1"
        ].getService(Components.interfaces.nsINavHistoryService);

        // No query options set will get all history, sorted in database order,
        // which is nsINavHistoryQueryOptions.SORT_BY_NONE.
        var options = historyService.getNewQueryOptions();
        // return one entry for each time a page was visited matching the 
        // given query.
        options.resultType = Components.interfaces
            .nsINavHistoryQueryOptions.RESULTS_AS_VISIT;

        // No query parameters will return everything
        var query = historyService.getNewQuery();
        query.beginTimeReference = query.TIME_RELATIVE_EPOCH;
        query.beginTime = timestamp * 1000000;

        // execute the query
        // result is instance of nsINavHistoryResult
        var result = historyService.executeQuery(query, options);
        
        var history = new Array();
        var cont = result.root;
        cont.containerOpen = true;
        
        for (var i = 0; i < cont.childCount; i ++) {

            var node = cont.getChild(i);
            // "node" attributes contains the information
            // (e.g. uri, title, time, icon...)
            // see : https://developer.mozilla.org/en/nsINavHistoryResultNode
            var entry = new Array();
            entry[0] = node.time;
            entry[1] = node.uri;
            entry[2] = node.title;
            //~ entry[3] = node.icon;
            history.push((entry));
            
        }
        
        // Close container when done
        // see : https://developer.mozilla.org/en/nsINavHistoryContainerResultNode
        cont.containerOpen = false;

        var appcontent = document.getElementById("appcontent"); // browser
        if (appcontent) {
            appcontent.addEventListener(
                "DOMContentLoaded", ZeitgeistExtension.onPageLoad, true
            );
            debug("successfully registered onPageLoad listener");
        }
        
        //~ var content = unescape(encodeURIComponent(history.toString()));
        var content = unescape(encodeURIComponent(history.toSource()));
                
        var fileStream = Components.classes[
            "@mozilla.org/network/file-output-stream;1"
        ].createInstance(Components.interfaces.nsIFileOutputStream);

        var header = "{\"bulk\": ";
        var footer = "}";

        fileStream.init(tmpfile, -1, -1, 0);
        fileStream.write(header, header.length);
        fileStream.flush();
        fileStream.write(content, content.length);
        fileStream.flush();
        fileStream.write(footer, footer.length);
        fileStream.flush();
        fileStream.close();
        var current_profile = ZeitgeistExtension.getProfileName();
        
        var args = ["--bulk", "--iofile", tmpfile.path, "--tags",
            unescape(encodeURIComponent(current_profile))
        ];
        
        debug("sending "+history.length+" events to the zeitgeist engine");
        ZeitgeistExtension.runScript(args);
        
    },

    onPageLoad: function(aEvent) {
        var doc = aEvent.originalTarget; // doc is document that triggered 
                                         // "onload" event
        // we don't care about iframes and such
        if (doc != doc.defaultView.top.document || 
            doc.documentURIObject.schemeIs("about")) return;

        debug("triggered onload event for: "+doc.location);
        
        // only log events in non-private mode
        var pbs = Components.classes[
            "@mozilla.org/privatebrowsing;1"
        ].getService(Components.interfaces.nsIPrivateBrowsingService);  
        var inPrivateBrowsingMode = pbs.privateBrowsingEnabled;  
        if (inPrivateBrowsingMode) {
            debug("Don't send events to zeitgeist in private mode");
            return;
        }
        
        // do something with the loaded page.
        // doc.location is a Location object (see below for a link).
        // You can use it to make your code executed on certain pages only.
        var current_profile = ZeitgeistExtension.getProfileName();
        
        var args = [
            "--location", unescape(encodeURIComponent(doc.location)),
            "--title", unescape(encodeURIComponent(doc.title)),
            "--tags", unescape(encodeURIComponent(current_profile)),
        ];
      
        ZeitgeistExtension.runScript(args);
    },
    
    getProfileName: function() {
        // get profile name (we will use it as a tag)
        const PROFILE_MANAGER = Components.classes[
             "@mozilla.org/toolkit/profile-service;1"
        ].getService(Components.interfaces.nsIToolkitProfileService);
        try {
            return PROFILE_MANAGER.selectedProfile.QueryInterface(
                Components.interfaces.nsIToolkitProfile
            ).name;
        } catch (error) {
            log_console("error while getting profile name: "+error);
            Components.utils.reportError(
                "error while getting profile name: "+error
            );
            return "unknown";
        }
    },
        
    runScript: function(args, callback) {
        // find the script within the extension
        const DIR_SERVICE = Components.classes[
            "@mozilla.org/extensions/manager;1"
        ].getService(Components.interfaces.nsIExtensionManager);
                
        try {
            var zeitgeist = DIR_SERVICE.getInstallLocation(
                "zeitgeist@zeitgeist-project.com"
            ).getItemFile(
                "zeitgeist@zeitgeist-project.com", 
                "chrome/content/zeitgeist-wrapper"
            );
        } catch (error) {
            log_console("error finding zeitgeist.py: "+error);
            Components.utils.reportError("error finding zeitgeist.py: "+error);
            return;
        }
        
        // create an nsILocalFile for the executable
        var file = Components.classes["@mozilla.org/file/local;1"]
                     .createInstance(Components.interfaces.nsILocalFile);
        try {
            file.initWithPath(zeitgeist.path);
            // see : http://blog.mozilla.com/addons/2010/01/22/broken-executables-in-extensions-in-firefox-3-6/
            file.permissions = 0755;
        } catch (error) {
            log_console("error finding zeitgeist.py: " + error);
            Components.utils.reportError("error finding zeitgeist.py: "+error);
            return;
        }

        // create an nsIProcess
        var process = Components.classes["@mozilla.org/process/util;1"]
                        .createInstance(Components.interfaces.nsIProcess);
        try {
            process.init(file);
        } catch (error) {
            log_console("error finding zeitgeist.py: " + error);
            Components.utils.reportError("error finding zeitgeist.py: "+error);
            return;            
        }
        if (!callback) {
            options = {
                observe: function(p, finishState, unused_data) {
                    var err_code = p.QueryInterface(Components.interfaces.nsIProcess).exitValue;
                    switch (err_code) {
                        case 0:
                            break;
                        case 100:
                            Components.utils.reportError(
                                "Zeitgeist daemon is not running and can not be launched"
                            );
                            break;
                        default:
                            // need to find the name of the iofile
                            // otherwise there is no chance to get the traceback
                            var tmpfile;
                            var x;
                            for (x in args) {
                                if (args[x] == "--iofile") {
                                    break
                                };
                            };
                            if (x < (args.length - 1)) {
                                var a =++ x;
                                var filename = args[a];
                                var tmpfile = Components.classes["@mozilla.org/file/local;1"]
                                    .createInstance(Components.interfaces.nsILocalFile);
                                try {
                                    tmpfile.initWithPath(filename);
                                } catch (error) {
                                    Components.utils.reportError("error finding traceback: "+error);
                                    break;
                                }
                                var traceback = getTraceback(tmpfile);
                                Components.utils.reportError(
                                    "Unknown Zeitgeist Error"+err_code+"\nTraceback\n"+traceback
                                );
                                break;
                            } else {
                                Components.utils.reportError(
                                    "Unknown Zeitgeist Error"+err_code+"\n(this might be in InsertEvents, we don't have an error handler for this yet)"
                                );
                                break;
                            };
                    }
                },
            };
        } else {
            options = {observe: callback};
        };
        
        // Run the process.
        // If first param is true, calling thread will be blocked until
        // called process terminates.
        // Second and third params are used to pass command-line arguments
        // to the process.
        process.runAsync(args, args.length, options);
    }
}
