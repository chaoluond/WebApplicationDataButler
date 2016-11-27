/* Wait until the DOM loads by wrapping our code in a callback to $. */
$(function() {
  $('#delete-button').click(function(event){
    var result = confirm("Are you sure to delete this file?");
    if (result == false) {
    	event.preventDefault();
    }
      
  });
});




