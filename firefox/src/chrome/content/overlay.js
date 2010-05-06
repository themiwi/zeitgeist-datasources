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
//                2010 Michal Hruby <michal.mhr@gmail.com>

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
    uriInfo: [],

    init: function() {
        debug("init zeitgeist extension");
        var appcontent = document.getElementById("appcontent");   // browser
        if (appcontent) {
            appcontent.addEventListener(
                "DOMContentLoaded", ZeitgeistExtension.onPageLoad, true
            );
            debug("successfully registered onPageLoad listener");
            ZeitgeistExtension.monitorHistory();
            ZeitgeistExtension.monitorDownloads();
        }
    },
    
    onPageLoad: function(aEvent) {
        var doc = aEvent.originalTarget; // doc is document that triggered 
                                         // "onload" event
        // we don't care about iframes and such
        if (doc != doc.defaultView.top.document || 
            doc.documentURIObject.schemeIs("about")) return;

        //debug("triggered onLoad event for: "+doc.location);
        
        // only log events in non-private mode
        var pbs = Components.classes[
            "@mozilla.org/privatebrowsing;1"
        ].getService(Components.interfaces.nsIPrivateBrowsingService);  
        var inPrivateBrowsingMode = pbs.privateBrowsingEnabled;
        if (inPrivateBrowsingMode) {
            return;
        }

        var info = ZeitgeistExtension.uriInfo[doc.documentURIObject.spec];
        if (!info) {
            info = new Array();
            ZeitgeistExtension.uriInfo[doc.documentURIObject.spec] = info;
        }

        info["title"] = unescape(encodeURIComponent(doc.title));
        info["mimetype"] = doc.contentType;
        info["loaded"] = true;

        if (info["visited"]) {
            ZeitgeistExtension.sendPageVisit(doc.documentURIObject, info);
            // we're done delete this info
            ZeitgeistExtension.uriInfo[doc.documentURIObject.spec] = null;
        }
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
    },

    sendPageVisit: function(uri, pageInfo) {
        var current_profile = this.getProfileName();

        var title = pageInfo["title"];
        var mimetype = pageInfo["mimetype"];
        
        debug("sending page visit: " + uri.spec + "[" +mimetype+ "] " + title);
        var args = [
            "--location", unescape(encodeURIComponent(uri.spec)),
            "--title", title,
            "--mimetype", mimetype,
            "--tags", unescape(encodeURIComponent(current_profile)),
        ];

        this.runScript(args);
    },

    monitorHistory: function() {
        var historyService = Components.classes[
            "@mozilla.org/browser/nav-history-service;1"
        ].getService(Components.interfaces.nsINavHistoryService);

        historyService.addObserver({
            onBeforeDeleteURI : function (uri) {},
            onBeginUpdateBatch : function () {},
            onClearHistory : function () {},
            onDeleteURI : function (uri) {},
            onEndUpdateBatch : function () {},
            onPageChanged : function (uri, what, val) {},
            onPageExpired : function (uri, visitTime, whole) {},
            onTitleChanged : function (uri, pageTitle) {},
            onVisit : function (uri, visitId, time, sessionId, referId, tt) {
                ZeitgeistExtension.pageVisited(uri, time);
            }
        }, false);
    },

    pageVisited: function(uri, time) {
        // only log events in non-private mode
        var pbs = Components.classes[
            "@mozilla.org/privatebrowsing;1"
        ].getService(Components.interfaces.nsIPrivateBrowsingService);  
        var inPrivateBrowsingMode = pbs.privateBrowsingEnabled;  
        if (inPrivateBrowsingMode) {
            return;
        }

        var info = ZeitgeistExtension.uriInfo[uri.spec];
        if (!info) {
            info = new Array();
            ZeitgeistExtension.uriInfo[uri.spec] = info;
        }

        info["visited"] = true;

        if (info["loaded"]) {
            ZeitgeistExtension.sendPageVisit(uri, info);
            // we're done delete this info
            ZeitgeistExtension.uriInfo[uri.spec] = null;
        }
    },

    monitorDownloads: function() {
        var downloadManager = Components.classes[
            "@mozilla.org/download-manager;1"
        ].getService(Components.interfaces.nsIDownloadManager);
        
        downloadManager.addListener({
            onSecurityChange : function (prog, req, state, dl) {},
            onProgressChange : function (prog, req, progCur, progMax, tProg, tProgMax,dl) {},
            onStateChange : function (prog, req, flags, status, dl) {},
            onDownloadStateChange : function (state, dl) {
                if (dl.state == Components.interfaces.nsIDownloadManager.DOWNLOAD_FINISHED) {
                    ZeitgeistExtension.downloadFinished (dl);
                }
            }
        });
    },

    downloadFinished: function(download) {
        var path = download.targetFile.QueryInterface(
            Components.interfaces.nsIFile).path;
        var title = download.displayName;
        debug("download finished for: " + title + " [" + path + "]");
        this.runScript(["--download", "--location", path, "--title", title]);
    }
}
