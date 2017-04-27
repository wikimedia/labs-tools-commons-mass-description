var data_offset = 0;
var removeFirstSlide = false;

addDescription = function() {

	var desc = $('#descript').val();
	$('#descript').val('');
	if(desc != "")
	{
		//add class remove to remove this element after trigger click on .right
		$('.active').addClass('remove');
		$(".right").click();
		$( ".remove" ).remove();

		//escape spaces
		for (p in desc)
		{
			if( p == " ")
			{
				p = "%20";
			}
		}

		data = desc;
		$.get("https://tools.wmflabs.org/commons-mass-description/edit?image=User:Martin_Urbanec/sand&description=" + data, function ( json ) {
			//console.log(json['status']);
			if(json['status'] == 'ok')
			{
				console.log('edited');
				$('.alert-success').removeClass('hidden');
				setTimeout(fade_out_success, 3000);
			}else {
				console.log('error');
				$('.alert-danger').removeClass('hidden');
			}
		});
	}
	else {
		$('.alert-warning').removeClass('hidden');
		setTimeout(fade_out_warning, 3000);
	}
};

getItems = function() {
	console.log(data_offset);
	$.get("https://tools.wmflabs.org/commons-mass-description/images?offset=" + data_offset, function( json ) {
		for (var i = 0; i < json.length; i++) {
			if(i != 9){
				addItemToCarousel(json[i]['url'], json[i]['title'], false);
			}
			else {
				addItemToCarousel(json[i]['url'], json[i]['title'], true);
			}
		}
	});
};
addItemToCarousel = function(url, caption, lastElement) {
	if (lastElement == true) {
		$( "<div class=\"item lastElement\"><img src=\"" + url + "\"><div class=\"carousel-caption width=\"1280\" height=\"720\" \">" + caption + "</div></div>" ).insertBefore( ".listovani" );
	}else {
		$( "<div class=\"item\"><img src=\"" + url + "\"><div class=\"carousel-caption width=\"1280\" height=\"720\" \">" + caption + "</div></div>" ).insertBefore( ".listovani" );
	}
};

checkLast = function() {
	var temp = $('.active');
	if (temp.hasClass('lastElement') == true)
	{
		$('.active').removeClass('lastElement');
		getItems();
	}
}

offset = function(left_or_right) {
	if(left_or_right == "+") {
		data_offset += 1;
	}else if(left_or_right == "-") {
		data_offset -= 1;
	}
}

function fade_out_success() {
	$(".alert-success").fadeOut().empty();
	$(".alert-success").addClass("hidden");
}

function fade_out_warning() {
	$(".alert-warning").fadeOut().empty();
	$(".alert-success").addClass("hidden");
}

$( document ).ready(function() {

	$('#maincarousel').carousel({ interval: 500, wrap: false });
	$('#maincarousel').carousel('pause');
	getItems();
	$( ".submit" ).click(function() {
		 addDescription();
	});

	//handle carousel clicks
	$(".left").click(function () {
		offset("-");
	});

	$(".right").click(function () {
		checkLast();
		offset("+");
		//remove first slide
		$("#hs").removeClass('hidden');
		//$(".firstSlide").hide();
		if (removeFirstSlide == true)
		{
			//$(".firstSlide").remove();
			$("div.firstSlide").remove()
		}
		removeFirstSlide = true;
	});

});
