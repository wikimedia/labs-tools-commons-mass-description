var entityMap = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
  '/': '&#x2F;',
  '`': '&#x60;',
  '=': '&#x3D;'
};

function escapeHtml (string) {
  return String(string).replace(/[&<>"'`=\/]/g, function (s) {
	return entityMap[s];
  });
}


$.getJSON('https://tools.wmflabs.org/commons-mass-description/api-langs', function (data) {
	for (var i = 0; i < data['langs'].length; i++) {
		if (data['langs'][i]['code'] == 'cs') {
			var row = '<option value="' + data['langs'][i]['code'] + '" selected>' + data['langs'][i]['name'] + '</option>';
		}
		else {
			var row = '<option value="' + data['langs'][i]['code'] + '">' + data['langs'][i]['name'] + '</option>';
		}
		$('#langs').append(row);
	}
})

function sendForm() {
	swal("Vaše data právě zpracováváme");
	$('button')[0].disabled = true;
}

function fillPics() {
	var url = 'https://tools.wmflabs.org/commons-mass-description/api-images?offset=' + $('#offset').text()
	$.getJSON(url, function (data) {
		for (var i = 0; i < data.images.length; i++) {
			var image = data.images[i];
			$('tbody').append('<tr><td><img src="' + image.thumburl + '"></td><td><input type="text" name="description-' + image.id + '"></td></tr>');
		}
		$('button')[0].disabled = false;
	});
}
fillPics();
