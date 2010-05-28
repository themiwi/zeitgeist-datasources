var plugin = document.embeds[0];

function onTabCreated (tab) {
}

function onTabRemoved (tabid) {
	// TODO: unfocus event?
}

function onTabUpdated (tabid, changeInfo, tab) {
	if (changeInfo.status == "complete") {
		/* FIXME:
		 *   What is this good for when it can't give us more info 
		 *   than what we already have here in 'tab'?
		 *
		 * At least we can try to use it to get rid of multiple events
		 * for just one webpage...
		 */
		chrome.tabs.executeScript(tabid, {file: "content_script.js"});
	}
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

chrome.tabs.onUpdated.addListener (onTabUpdated);
chrome.tabs.onCreated.addListener (onTabCreated);
chrome.tabs.onRemoved.addListener (onTabRemoved);
chrome.extension.onConnect.addListener (onExtensionConnect);

plugin.setActor("application://google-chrome.desktop");
