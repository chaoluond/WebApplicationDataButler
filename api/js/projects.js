/* Wait until the DOM loads by wrapping our code in a callback to $. */
$(function() {
  // disable the context menu
  document.oncontextmenu = function() {return false;};

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
}
);

  $('.delete').click(function(event) {
	var del = $(this);
	event.preventDefault();
   	$.ajax({
		url: del.attr('href'),
		type: 'DELETE'
	});	
	$(document).ajaxStop(function(){
   		 window.location.reload();
	});
   });
	


});

