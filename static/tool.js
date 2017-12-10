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
	var images = $('input');
	var language = $('#langs').val();
	var payload = [];
	for (var i = 0; i < images.length; i++) {
		var image = images[i];
		var id = Number(image.name.replace('description-', ''));
		var description = image.value;
		if (description!='') {
			var imagepayload = {
				'id': id,
				'description': description,
				'lang': language,
			};
			payload.push(imagepayload);
			console.log(id);
		}
	}
	$.postJSON('https://tools.wmflabs.org/commons-mass-description/api-edit', payload, function (data) {
		console.log(data);
		//fillPics();
		//$('button')[0].disabled = false;
	})
}

function fillPics() {
	var url = 'https://tools.wmflabs.org/commons-mass-description/api-images?offset=' + $('#offset').text();
	var url = 'https://tools.wmflabs.org/commons-mass-description/api-images';
	$.getJSON(url, function (data) {
		for (var i = 0; i < data.images.length; i++) {
			var image = data.images[i];
			$('tbody').append('<tr><td><a href="' + image.url + '" data-lightbox="image-' + image.id + '"><img src="' + image.thumburl + '"></a></td><td><input type="text" name="description-' + image.id + '"></td></tr>');
		}
		$('button')[0].disabled = false;
	});
}
fillPics();
