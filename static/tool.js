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
