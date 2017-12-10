String.prototype.replaceAll = function(search, replacement) {
	var target = this;
	return target.split(search).join(replacement);
};

$.postJSON = function(url, data, callback) {
	return jQuery.ajax({
		'type': 'POST',
		'url': url,
		'contentType': 'application/json',
		'data': JSON.stringify(data),
		'dataType': 'json',
		'success': callback
	});
};

$( document ).ready(function() {
	$.getJSON('https://tools.wmflabs.org/commons-mass-description/api-username', function (data) {
		$('#username').text(data['username']);
	});
});
