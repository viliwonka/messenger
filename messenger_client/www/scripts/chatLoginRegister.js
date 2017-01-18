var chatAPI = chatAPI || {}

$(function() {

   var loginFormLink     = $('#login-form-link');
   var registerFormLink  = $('#register-form-link');

   var loginForm         = $("#login-form");
   var registerForm      = $("#register-form");
   
   var registerButton    = $("#register-submit");
   var loginButton       = $("#login-submit");

   var _usernameBox      = $("#registerUsername")
   var _passBox          = $("#registerPassword")

   registerButton.click(function(e){
      //chatAPI.registerNewUser = function(username, password, countryCode, callback) {

      var _username       = _usernameBox.val()
      var _country        = $("#countrySelector").val()
      var _confirmPassBox = $("#registerConfirm-password")

      var _pass           = _passBox.val()
      var _confirmPass    = _confirmPassBox.val()
     
      console.log("usernm"+_username)
      console.log("country"+_country)
      console.log("pass"+_pass)
      console.log("passcnfrm"+_confirmPass)

      if(_pass != _confirmPass) {
         alert("Password doesn't match-")
      }
      else if(_username.length < 6) {

         alert("Username too short, minimum length is 6")
      }
      else if(_username.length > 32) {
         alert("Username too long, maximum length is 32")
      }
      else if(_pass.length < 6) {
         alert("Password too short, minimum length is 6")
      }
      else if(_pass.length > 40) {
         alert("Password too long, maximum length is 40")
      }
      else {

         chatAPI.registerNewUser(_username, _pass, _country, function(result){
            //rezultat registracije
            if(result=="ok"){
               alert("Registration sucessful! Now login");

               loginFormLink.click()
            }
            else{
               alert("Registration unsucessful! Username already taken")
            }
         })
      }
   });

   loginButton.click(function(e){
      //chatAPI.login = function(username, password, callback) {

      var _username = $("#loginUsername").val()
      var _pass     = $("#loginPassword").val()
     
      console.log("usernm"+_username)
      console.log("pass"+_pass)

      chatAPI.login(_username, _pass, function(result){
         //rezultat registracije
         if(result == "ok")
         {
            alert("Login sucessful!!");
         }
         else if(result == "wrong") 
         {
            alert("Wrong username or password")
         } 
         else {
            alert("Error on server!")
         }
      })
      
   });

   loginFormLink.click(function(e) {

      loginForm.show().delay(100).fadeIn(100);
      registerForm.hide().fadeOut(100);
      registerFormLink.removeClass('active');
      $(this).addClass('active');
      e.preventDefault();
   });

   registerFormLink.click(function(e) {

      registerForm.show().delay(100).fadeIn(100);
      loginForm.hide().fadeOut(100);
      loginFormLink.removeClass('active');
      $(this).addClass('active');
      e.preventDefault();
   });
});