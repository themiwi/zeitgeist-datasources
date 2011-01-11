var plugin = document.embeds[0];

function onTabCreated (tab) {
	chrome.tabs.executeScript(tab.id, {file: "content_script.js"});
}

function onTabRemoved (tabid) {
	// TODO: unfocus event?
}

function onTabUpdated (tabid, changeInfo, tab) {
	if (!changeInfo.url) return;
	chrome.tabs.executeScript(tabid, {file: "content_script.js"});
}

function onBookmarkCreated (bookmarkid, bookmark) {
	if (!bookmark.url) return; // bookmark folder
	var url = bookmark.url;
	var title = bookmark.title;
	var mimetype = "text/html"; // FIXME: really? use XHR to get it?
	plugin.insertEvent(url, url, mimetype, title, plugin.BOOKMARK);
}

function sendAccessEvent (documentInfo) {
	var url = documentInfo.url;
	var origin = documentInfo.origin;
	var mimetype = documentInfo.mimeType;
	var title = documentInfo.title;
	plugin.insertEvent(url,
	                   origin ? origin : url,
	                   mimetype ? mimetype : "text/html",
	                   title);
}

// yea, this worked in chrome 5
function onExtensionConnect (port) {
	port.onMessage.addListener(
		function(message) {
			sendAccessEvent(message);
		}
	);
}

// and this works in chrome 7
function onExtensionRequest (request, sender, sendResponse) {
	sendAccessEvent(request);
}

var is_chromium = /chromium/.test( navigator.userAgent.toLowerCase() );
if (!is_chromium) plugin.setActor("application://google-chrome.desktop");
else plugin.setActor("application://chromium-browser.desktop");

//chrome.extension.onConnect.addListener (onExtensionConnect);
chrome.extension.onRequest.addListener (onExtensionRequest);
chrome.bookmarks.onCreated.addListener (onBookmarkCreated);
chrome.tabs.onUpdated.addListener (onTabUpdated);
chrome.tabs.onCreated.addListener (onTabCreated);
chrome.tabs.onRemoved.addListener (onTabRemoved);

chrome.tabs.getAllInWindow(null, function (tabs) {
	for (var i=0; i<tabs.length; i++)
		chrome.tabs.executeScript(tabs[i].id, {file: "content_script.js"});
});
