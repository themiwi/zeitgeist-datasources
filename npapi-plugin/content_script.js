function zgGetContentTypeFromHeader() {
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
			return content_type.split(';')[0];
		}
	}
	return null;
}

function zgGetDocumentInfo () {
	var docInfo = {
		"url": document.URL,
		"title": document.title
	};

	var contentType = zgGetContentTypeFromHeader();
	if (contentType) {
		docInfo["mimeType"] = contentType;
		chrome.extension.sendRequest({name: "zgPlugin"}, docInfo);
	} else {
		// send extra request to get the mime type
		var request = new XMLHttpRequest();
		request.open("HEAD", document.URL, true);
		request.onreadystatechange=function() {
			if (request.readyState==4) {
				var content = request.getResponseHeader("Content-Type");
				if (!content) return;
				docInfo["mimeType"] = content;
				chrome.extension.sendRequest({name: "zgPlugin"}, docInfo);
			}
		}
		request.send(null);
	}
}

if (document.readyState == "loading") {
	// seems like it never gets here...
	window.addEventListener("onload", zgGetDocumentInfo, false);
} else {
	zgGetDocumentInfo();
}
