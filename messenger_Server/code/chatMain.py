import psycopg2
import sys
import json

import datetime
import asyncio
from asyncio import coroutine
from os import environ

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

import sqlQueries

tokenToUsernameDict = {}
#WAMP API DEFINITIONS
class MyComponent(ApplicationSession):

	async def onJoin(self, details):
		
		global tokenToUsernameDict

		print("session joined")
		# can do subscribes, registers here e.g.:
		# yield from self.subscribe(...)
		# yield from self.register(...)
	
		# just example code for date
        # def utcnow():
        #    now = datetime.datetime.utcnow()
        #    return now.strftime("%Y-%m-%dT%H:%M:%SZ")
		def usernameExists(username):
			if type(username) is str:
				try:
					if sqlQueries.userExists(username):
						print("userExists, True") 
						return "true"
					else:
						print("userExists, False")
						return "false"
				except Exception as e:
					print("Error, exception:" + str(e))
					return "error"	
			else:
				print("Error \"usernameExists\": username or password are not strings")
				return "error"

		def registerNewUser(username, password, countryCode):
			if type(username) is str and type(password) is str and len(username) >= 6 and len(username) <= 32 and len(password) >= 6 and len(password)<= 40:
				print("----------------------------")
				print("Username: " + username)
				print("Password: " + password)
				print("countryCode " + countryCode)
				print("----------------------------")
				
				try:
					if not sqlQueries.userExists(username):
						result = sqlQueries.registerUser(username, password, countryCode)

						print("Result:" + str(result))
						print("User {} with pw \"{}\" has registered sucessfully".format(username, password))
						return "ok"
					else:
						print("User {} already exists.".format(username))
						return "alreadyExists"
				except Exception as e:
					print("Error \"registerNewUser\" exception:" + str(e))
					return "error"	
			else:
				print("Error \"registerNewUser\": username or password are not strings")
				return "error"

		def login(username, password):
			global tokenToUsernameDict
			if type(username) is str and type(password) is str:
				try:
					#preverimo, ali user obstaja in kasneje preverimo, ce se geslo ujema
					if sqlQueries.userExists(username):

						(success, token) = sqlQueries.authenticateUser(username, password)

						if success is True:
							#zapomni si zeton, zato da bo user lahko vedno posiljal svoj zeton
							tokenToUsernameDict[token] = username
							print("User {} with pw \"{}\" has logined sucessfully".format(username, password))					
							return ["ok", token]
						else:
							print("Wrong auth with username {}.".format(username))
							return ["wrong", ""]	
					else:
						print("Username {} does not exists.".format(username))
						return ["wrong", ""]
				except Exception as e:
					print("Error \"login\", exception:" + str(e))
					return ["error", ""]	
			else:
				print("Error \"login\": username or password are not strings")
				return ["error",""]

		#register functions
		await self.register(usernameExists, u'com.usernameExists')
		await self.register(registerNewUser, u'com.registerNewUser')
		await self.register(login, u'com.login')
		
		########################################################################
		#FRIENDSHIPPING
		########################################################################
		#search for friendship with this query, returns list of friends
		#username of person that is doing query
		def searchRooms(username, query):
			pass
			
		def searchUsers(username, query):
			return sqlQueries.searchUsername(username, query)
		
		await self.register(searchUsers, u'com.searchUsers')
		
		#request friendship with this query
		#username of person that is doing query
		#targetPerson is person that we are requesting friendship from
		def requestFriendship(username, targetPerson):

			(status, origCaller) = sqlQueries.getFriendshipStatus(username, targetPerson)

			#target person already sent request
			if status == sqlQueries.fRequest and origCaller == targetPerson:
				sqlQueries.setFriendshipStatus(username, targetPerson, sqlQueries.fAccepted)
			else:
				sqlQueries.setFriendshipStatus(username, targetPerson, sqlQueries.fRequest)

			return True

		await self.register(requestFriendship, u'com.requestFriendship')
		#accept or ignore friend with this query
		#username of person that is doing accept/ignore to targetPerson
		#uses tables: user, friendship, participates, chatroom
		def acceptFriendship(username, targetPerson, acceptElseIgnore):
 
			(status, origCaller) = sqlQueries.getFriendshipStatus(username, targetPerson)

			if status == sqlQueries.fRequest and origCaller == targetPerson:
				sqlQueries.setFriendshipStatus(username, targetPerson, sqlQueries.fRequest)
				return True
			else:
				return False

		await self.register(acceptFriendship, u'com.acceptFriendship')
		#gets list of all friends and also their status (friended, waitingYouForAccept, waitingHimForAccept)
		def getAllFriends(username):
			return sqlQueries.getAllFriends(username)

		await self.register(getAllFriends, u'com.getAllFriends')
		#########################################################################
		#MESSAGING
		#########################################################################
		#send message to room/friend, also save it to database
		def sendMessage(chatroomName, username, text, timestamp):
			return False

		def getMessages(chatroomName, username, from_timestamp, to_timestamp):
			pass

		#########################################################################
		#ROOMS
		########################################################################

		#not an actual query, but useful function that converts friendship chat to room
		def friendshipToRoomName(friend1, friend2):
			arr = [friend1, friend2]
			arr.sort()
			return arr[0] + "____" + arr[1]

		#uses tables: user, participates, chatroom
		def createRoom(username, roomName):
			#ignore now
			pass

		#uses tables: user, participates, chatroom
		def joinRoom(username, roomName):
			#ignore now
			pass

		#find rooms that are public
		# uses tables: chatroom
		def searchPublicRoom(username, query):
			#ignore now
			pass

		def inviteToRoom(username, roomName, targetPerson):
			#ignore now
			pass

		sqlQueries.setFriendshipStatus("kmetkmet", "drekdrek", "Accepted")
		print(str(sqlQueries.getAllFriends("kmetkmet")))
if __name__ == '__main__':

	print("Connecting to database")

	try:
		sqlQueries.connectDatabase()

	except Exception as e:
		print(e)

	print("Running server component.")

	try: 
		runner = ApplicationRunner(url=u"ws://127.0.0.1:8080/ws", realm=u"realm1")
		runner.run(MyComponent)

	except Exception as e:
		print(e)