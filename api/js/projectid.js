/* Wait until the DOM loads by wrapping our code in a callback to $. */
$(function() {
  // disable the context menu
  document.oncontextmenu = function() {return false;};

  /* Add click event listeners to the restaurant list items. This adds a
 *    * handler for each element matching the CSS selector
 *       * .restaurant-list-item. */
  $('a.link-in-list').mousedown(function(event) {
    if (event.which == 3){

    /* Prevent the default link navigation behavior. */
    event.preventDefault();
   
    var $project = $(this);
    var $actions = $project.siblings('.action-sublist');



    /* If the menu list is shown, hide it. */
    if($actions.is(':visible')) {
      $actions.slideUp();
      return;
    }
    
    $('.action-sublist').not($actions).slideUp()

    $actions.slideDown();
    }
  });

  $('#upload').on('click',function(event) {
 	event.preventDefault();
	var uploadform = $('.upload-form');
	uploadform.slideToggle();	
  });
});
