import psycopg2
import sys
import json
import hashlib
import bcrypt

import datetime
import asyncio
from asyncio import coroutine
from os import environ

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
import random
import string

dbConn = None

def connectDatabase():

	global dbConn

	conn_string = "host='localhost' dbname='messenger' user='postgres' password='rolebole777'"
	print("Connecting to database\n ->%s" % (conn_string))
	dbConn = psycopg2.connect(conn_string)

	print("Connected!")

def disconnectDatabase():
	dbConn.close()
# TO JE TUKAJ SAMO ZA INFO O TABELI
"""
CREATE TABLE public.user (
    username varchar(64) NOT NULL,
    password_hash varchar(64) NOT NULL,
    email varchar(255) NOT NULL,
    lastonline timestamp without time zone NOT NULL,
    countryid integer NOT NULL,
    registertime timestamp with time zone NOT NULL,
    status varchar(32),
    PRIMARY KEY (username)
);
"""

#return TRUE OR FALSE
def userExists(username):

	SQL = """SELECT count(username) FROM public.User GROUP BY username HAVING (username) = %(username)s """
	data = { 'username': username }

	with dbConn.cursor() as curs:
		curs.execute(SQL, data)
		data = curs.fetchall()
		dbConn.commit()
		if len(data) == 0:
			return False
		else:
			return True

#return TRUE OR FALSE
def authenticateUser(username, password):

	SQL = """SELECT password_hash FROM public.User WHERE username = %(username)s"""
	
	data = { 'username': username }

	with dbConn.cursor() as curs:
		curs.execute(SQL, data)
		data = curs.fetchall()
		dbConn.commit()

		if len(data) == 0:
			print("len(data) == 0 in authenticateUser")
			return False

		password_hash = data[0][0]

		print("HERE:" + str(data) + ".." + str(type(data)))

		encoded = password_hash.encode('UTF_8')

		success = (bcrypt.hashpw(password.encode('UTF_8'), encoded) == encoded)

		if success:
			token = username.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
			return (True, token)
		else:

			return (False, '')

#return True or False
def registerUser(username, password, countrycode):

	SQL = """INSERT INTO public.User (username, password_hash, lastonline, countrycode, registertime, status) VALUES (%(username)s, %(hash)s, %(reg_time)s, %(countryid)s, %(reg_time)s, %(status)s)"""

	pw_hash = bcrypt.hashpw(password.encode('UTF_8'), bcrypt.gensalt())

	now = datetime.datetime.utcnow()
	registerTime = now.strftime("%Y-%m-%dT%H:%M:%SZ")

	data = {

		'username'		: username, 
		'hash' 			: str(pw_hash, 'UTF_8'),
		'reg_time' 		: registerTime,
		'countryid'		: countrycode,
		'status'		: "NULL"
	}

	try:
		with dbConn.cursor() as curs:
			curs.execute(SQL, data)
			print(str(curs.fetchall()))
			dbConn.commit()
			return True
	except Exception as e:

		print(str(e))

		return False
	
########################################################################
#FRIENDSHIP
########################################################################
#search for friendship with this query, returns list of friends
#username of person that is doing query
def searchUsername(searcher, query):
		
	SQL = """SELECT username FROM public.User WHERE username LIKE %%%(query)s%% AND username != %(searcher)s ORDER BY username"""

	data = {
		'query' 	: query,
		'searcher' 	: searcher
	}

	try:
		with dbConn.cursor() as curs:
			curs.execute(SQL, data)

			searchResult = curs.fetchall()	

			print("searchUsername: \n" + str(searchResult))
			dbConn.commit()

			return searchResult
	except Exception as e:
		print("searchUsername error: " + str(e))
		return []

# request friendship with this query
# username of person that is doing query
# targetPerson is person that we are requesting friendship from

fRequest  = "Request"
fIgnore   = "Ignore"
fAccepted = "Accepted"

friendStatus = [fRequest, fIgnore, fAccepted]

def setFriendshipStatus(thisUsername, targetUsername, status):

	global friendStatus
	global fRequest
	global fIgnore
	global fAccepted

	arr = [thisUsername, targetUsername]
	arr.sort()
	SQL = """INSERT INTO public.friendship AS fs (Username_1, Username_2, Status) 
	VALUES (%(UserOne)s, %(UserTwo)s, %(Status)s) 
	ON CONFLICT (Username_1, Username_2) 
	DO UPDATE SET Status = %(Status)s	
	WHERE fs.Username_1 = %(UserOne)s AND fs.Username_2 = %(UserTwo)s """

""" INSERT INTO public.friendship as pf (Username_1, Username_2, Status) 
	VALUES ('User1', 'User2', 'Accepted') 
	ON CONFLICT (Username_1, Username_2) 
	DO UPDATE SET (Status) = ('Accepted')	
	WHERE pf.Username_1 = 'User1' AND pf.Username_2 = 'User2';
"""
	# preverimo ce je status sploh pravi
	if status in friendRequest:
		stat = status
		if stat == fRequest or stat == fIgnore
			int num = 0 if (arr[0] == thisUsername) else 1
			stat = stat + str(num)

		data = {
			'UserOne' : arr[0],
			'UserTwo' : arr[1],
			'Status'  : stat
		}
	else
		print("wrong status")
		throw new Exception("Wrong status")

def getFriendshipStatus(thisUsername, targetUsername):

	global friendStatus
	global fRequest
	global fIgnore
	global fAccepted

	arr = [thisUsername, targetUsername]
	arr.sort()

	SQL = """SELECT Username_1, Username_2, Status FROM public.friendship 
	WHERE Username_1 == %(username)s OR Username_2 == %(username)s"""

	#preverimo ce je status sploh pravi
	if status in friendRequest:
		stat = status
		if stat == fRequest or stat == fIgnore
			int num = 0 if (arr[0] == thisUsername) else 1
			stat = stat + str(num)

		data = {
			'UserOne' : arr[0],
			'UserTwo' : arr[1],
			'Status'  : stat
		}
	else
		print("wrong status")
		throw new Exception("Wrong status")


# accept or ignore friend with this query
# username of person that is doing accept/ignore to targetPerson
# uses tables: user, friendship, participates, chatroom
def acceptFriendship(thisUsername, targetPerson):
	global fAccepted
	setFriendshipStatus(thisUsername, targetPerson, fAccepted)

def ignoreFriendship(thisUsername, targetPerson):
	global fIgnore
	setFriendshipStatus(thisUsername, targetPerson, fIgnore)

def requestFriendship(thisUsername, targetPerson):
	global fRequest
	setFriendshipStatus(thisUsername, targetPerson, fRequest)



# gets list of all friends and also their status (friended, waitingYouForAccept, waitingHimForAccept)
def getAllFriends(username):
	
	SQL = """SELECT Username_1, Username_2, Status FROM public.friendship 
	WHERE Username_1 == %(username)s OR Username_2 == %(username)s"""

	data = {
		'username' : username
	}

	try:
		with dbConn.cursor() as curs:

			curs.execute(SQL, data)
			fetched = curs.fetchall()
			
			friendStatusList = []

			for tupple in fetched:

				if tupple[0] == username:
					friendStatusList += [tupple[1], tupple[2]]
				else:
					friendStatusList += [tupple[0], tupple[2]]

			print("getAllFriends: \n" + str(fetched))

			dbConn.commit()
			return friendStatusList
	except Exception as e:
		print("getAllFriends exception: \n" + str(e))
		return []

# ########################################################################
# MESSAGING
# ########################################################################
# send message to room/friend, also save it to database
def saveMessage(chatroomName, username, text, timestamp):
	
	pass

def getMessages(chatroomName, username, from_timestamp, to_timestamp):

	pass

# ########################################################################
# ROOMS
# #######################################################################

#not an actual query, but useful function that converts 
def friendshipToRoomName(friend1, friend2):
	arr = [friend1, friend2]
	arr.sort()
	return arr[0] + "____" + arr[1]

#uses tables: user, participates, chatroom
def createRoom(username, roomName):
	
	pass

#uses tables: user, participates, chatroom
def joinRoom(username, roomName):
	
	pass

#find rooms that are public
# uses tables: chatroom
def searchPublicRoom(username, query):
	
	pass

def inviteToRoom(username, roomName, targetPerson):

	pass

