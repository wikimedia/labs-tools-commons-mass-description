  getItems = function() {
    $.get("https://tools.wmflabs.org/commons-mass-description/images", function( json ) {
      for (var i = 0; i < json.length; i++) {
        //console.log(json[i]['url'], json[i]['title']);
        if(i != 8){
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

  $( document ).ready(function() {
    getItems();
    $( ".submit" ).click(function() {
      console.log("click");
    });

    //handle carousel clicks
    $(".left").click(function () {
      checkLast();
    });

    $(".right").click(function () {
      checkLast();
    });

  });
