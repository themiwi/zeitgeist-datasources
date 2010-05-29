var dict = {
	"url": document.URL,
	"title": document.title
};

function updateContentType() {
	var nodes = document.getElementsByTagName("meta");
	for (var i=0; i<nodes.length; i++)
	{
		var node = nodes[i];
		if (!node.hasAttributes()) continue;
		var http_equiv = node.getAttribute("http-equiv");
		if (http_equiv && http_equiv.toLowerCase() == "content-type")
		{
			var content_type = node.getAttribute("content");
			if (!content_type) continue;
			content_type = content_type.split(';')[0];
			dict["mimeType"] = content_type;
			return true;
		}
	}
	return false;
}

if (updateContentType()) {
	chrome.extension.sendRequest({name: "zgPlugin"}, dict);
} else {
	// send extra request to get the mime type
	var request = new XMLHttpRequest();
	request.open("HEAD", document.URL, true);
	request.onreadystatechange=function() {
		if (request.readyState==4) {
			var content = request.getResponseHeader("Content-Type");
			dict["mimeType"] = content;
			chrome.extension.sendRequest({name: "zgPlugin"}, dict);
		}
	}
	request.send(null);
}
