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
fillPics();

function fillPics() {
	$.getJSON('https://tools.wmflabs.org/commons-mass-description/api-images', function (data) {
		for (var i = 0; i < data['images'].length; i++) {
			var row = '<div class="imagerow"><tr><td><img class="image" alt="' + escapeHtml(data['images'][i]['title']) + '" src="' + data['images'][i]['thumburl'] + '"></td><td><input type="text" class="description" id="description-' + i + '"></td></div>';
			$('tbody').append(row);
			break;
		}
		$('button')[0].disabled = false;
	})
}
function sendForm() {
	var data = $('.description');
	$('tbody').empty();
	$('button')[0].disabled = true;
	swal("Momentálně vaše data zpracováváme!", "Počkejte, prosím!");
	var request = [];
	for (var i = 0; i < data.length; i++) {
		var rowdata = {};
		rowdata['description'] = data[i].value;
		rowdata['title'] = data[i].closest('.imagerow').children[0].alt;
		rowdata['lang'] = $('#langs')[0].value;
		request.push(rowdata);
	}
	$.ajax({
		type: 'POST',
		url: 'https://tools.wmflabs.org/commons-mass-description/api-edit',
		data: JSON.stringify(request),
		success: function (data) {
			console.log(data);
		},
		error: function (request, error) {
			console.log(error);
		}
		contentType: "application/json",
		dataType: "json"
	})
}
