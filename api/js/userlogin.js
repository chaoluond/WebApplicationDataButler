$(function() {
  function isValidEmail(email) {
    var re = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
    return re.test(email);
  }

  function isValidPassword(pwd) {
    // at least one number, one lowercase, one uppercase letter, one special symbol
    // at least nine characters
    var re = /(?=.*\d)(?=.*[a-zA-Z]).{8,}/;
    return re.test(pwd);
  }

  $('#sign-in-form').on('submit', function(event) { // form id

    var email = $('#user-email-input').val(); // input id
    var pwd = $('#user-password-input').val(); // input id

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

  });
});

