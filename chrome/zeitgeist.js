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

function onExtensionConnect (port) {
	port.onMessage.addListener(
		function(message) {
			var url = message.url;
			var mimetype = message.mimeType;
			var title = message.title;
			plugin.insertEvent(url,
			                   mimetype ? mimetype : "text/html",
			                   title);
		}
	);
}

plugin.setActor("application://google-chrome.desktop");

chrome.extension.onConnect.addListener (onExtensionConnect);
chrome.tabs.onUpdated.addListener (onTabUpdated);
chrome.tabs.onCreated.addListener (onTabCreated);
chrome.tabs.onRemoved.addListener (onTabRemoved);

chrome.tabs.getAllInWindow(null, function (tabs) {
	for (var i=0; i<tabs.length; i++)
		chrome.tabs.executeScript(tabs[i].id, {file: "content_script.js"});
});
