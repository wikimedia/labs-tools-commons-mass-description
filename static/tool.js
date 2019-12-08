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

function sendForm() {
	swal("Your data are being processed right now");
	$('#send').disabled = true;
	var images = $("input[name^='description-']");
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
	$.postJSON('api-edit', payload, function (data) {
		console.log(data);
		fillPics();
		$('button')[0].disabled = false;
	})
}

function fillPics() {
	$('tbody').empty();
	$('#send')[0].disabled = true;
	$('#search')[0].disabled = true;
	var filter = "";
	var filtera = $('input:checked[name="filter"]').val();
	if (filtera == "nofilter") {
		filter = "&category=Category:Media_lacking_a_description"
	} else if (filtera == "category") {
		filter = '&category=' + $('#category').val().replaceAll(' ', '_');
	} else if (filtera == "user") {
		filter = '&user=' + $('#user').val().replaceAll(' ', '_');
	}
	var url = 'api-images?display=' + $('#display').val() + filter;
	console.log(url);
	$.getJSON(url, function (data) {
		for (var i = 0; i < data.images.length; i++) {
			var image = data.images[i];
			$('tbody').append('<tr id="image-row-' + image.id + '"><td><a href="' + image.url + '" data-lightbox="image-' + image.id + '"><img src="' + image.thumburl + '"></a></td><td><input type="text" name="description-' + image.id + '"></td></tr>');
			fillCat(image.id)
		}
		$('#send')[0].disabled = false;
		$('#search')[0].disabled = false;
	});
}

async function fillCat(id) {
	var url = 'api-categories?pageid=' + id;
	$.getJSON(url, function (data) {
		var html = "<td><ul>";
		for (var i = 0; i < data.categories.length; i++) {
			html += '<li><a href="https://commons.wikimedia.org/wiki/' + data.categories[i] + '">' + data.categories[i] + '</a></li>';
		}
		html += "</ul></td>";
		$('#image-row-' + id).append(html);
	});
}

$( document ).ready(function() {
	fillPics();
});
