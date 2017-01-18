var chatAPI = chatAPI || {}

//run this code when whole page loads
$(function(){
 
   var Cookies2 = Cookies.noConflict();

   chatAPI.loginData = {

      username : Cookies2.get('login.username'),
      token    : Cookies2.get('login.token')
   }

   var connection = new autobahn.Connection({
            url: 'ws://fmf-chat.club:8080/ws',
            realm: 'realm1'
   });

   connection.onopen = function (session) {
      // 1) subscribe to a topic
      function onevent(args) {
         console.log("Event:", args[0])
      }

      chatAPI.logout = function() {
         chatAPI.loginData = {} //clear data
         Cookies2.remove('login.username')
         Cookies2.remove('login.token')
      }

      chatAPI.login = function(username, password, callback) {
         session.call('com.login', [username, password]).then(
            function (res) {
               
               console.log("res: " + res)

               token = res[1]

               chatAPI.loginData = {}
               chatAPI.loginData.username = username
               chatAPI.loginData.token    = token

               Cookies2.set('login.username', username)
               Cookies2.set('login.token'   , token)

               callback(res[0])
         })   
      }

      chatAPI.registerNewUser = function(username, password, countryCode, callback) {
         
         //Callback should return OK
         session.call('com.registerNewUser', [username, password, countryCode]).then(
            function (res) {
               console.log("Result from registerNewUser:", res)
               callback(res)
         })
      }

      chatAPI.usernameExists = function(username, callback) {
         //Callback should return TRUE or FALSE 
         session.call('com.usernameExists', [username]).then(
            function (res) {
               console.log("Result from login:", res)
               callback(res)
         })
      }
   }

   autobahn.Connection.onclose = function (reason, details) {
   // connection closed, lost or unable to connect
   // reason = "closed" or "lost" or "unreachable" or "unsupported"
   }

   connection.open()
})