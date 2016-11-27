$(function() {
  function isValidEmail(email) {
    var re = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
    return re.test(email);
  }

  function isValidPassword(pwd) {
    // at least one number, one lowercase, one uppercase letter, one special symbol
    // at least nine characters
    var re = /(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[?!_#%^&@-]).{9,}/;
    return re.test(pwd);
  }


  function isPasswordMatch(pwd, confpwd) {
    return (pwd == confpwd);
  }
  $('#user-add-form').on('submit', function(event) { // form id

    var email = $('#user-email-input').val(); // input id
    var pwd = $('#user-password-input').val(); // input id
    var confpwd = $('#user-confirm-password-input').val() // input id
	
    if(isValidEmail(email)) {
      $('#email-error').hide(); // div id
    } else {
      $('#email-error').text('Email must be in the correct format.').show();
      event.preventDefault();
    }

    if(isValidPassword(pwd)) {
      $('#password-error').hide(); // div id
    } else {
      $('#password-error').text('Password has to be 9 or more characters, and contain at least 1 upper case, 1 lower case, 1 number, and 1 symbol.').show();
      event.preventDefault();
    }
    
    if(isPasswordMatch(pwd, confpwd)) {
      $('#confirm-password-error').hide();
    } else {
      $('#confirm-password-error').text('Password and Confirm password do not match! Please enter again!').show();
      event.preventDefault();
    }


  });
});

