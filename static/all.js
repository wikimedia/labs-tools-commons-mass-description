$.getJSON('https://tools.wmflabs.org/commons-mass-description/api-username', function (data) {
	$('#username').text(data['username']);
});

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
