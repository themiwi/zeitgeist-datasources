var dict = {
	"url": document.URL,
	"mimeType": document.contentType,
	"title": document.title
};
chrome.extension.sendRequest({name: "zgPlugin"}, dict);
