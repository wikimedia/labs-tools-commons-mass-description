$.getJSON('https://tools.wmflabs.org/commons-mass-description/api-username', function (data) {
	$('#username').text(data['username']);
});
