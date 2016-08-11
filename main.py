"""`main` is the top level module for your Flask application."""

#import request to request data from client server
from flask import Flask, render_template, request, session, json
import operator
from operator import itemgetter
from datetime import datetime
#import for lumberjacking 
import logging, urllib2
from google.appengine.ext import ndb
import string
import base64
from base64 import standard_b64decode
import random
from functools import wraps
from flask import request, Response


app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

#This key is a secret.
app.secret_key = 'ServerDev_Assign1_140522J_AlmedaGlenn'

#your friendly global variable
sign_in = False

win = 0
lose = 0

class game_list(ndb.Model):
	word = ndb.StringProperty()
	hint = ndb.StringProperty()
	word_length = ndb.IntegerProperty()
	game_id = ndb.StringProperty()
	wins = ndb.IntegerProperty()
	losses = ndb.IntegerProperty()

#the user information, a kind
#it contains all the information related to the player
class account_info(ndb.Model):
	signed_in = ndb.BooleanProperty()
	username = ndb.StringProperty()
	password = ndb.StringProperty()
	token = ndb.StringProperty()
	games_created = ndb.IntegerProperty()
	games_played = ndb.IntegerProperty()
	games_won = ndb.IntegerProperty()
	games_lost = ndb.IntegerProperty()

def totalSessionCount():
	session['game_answer'] = ""				#the current game's answer here
	session['current_word_state'] = ""		#the current game's word state
	session['current_bad_guesses'] = 0		#the current game's bad guess count
	session['games_created'] = 0			#the number of games created player
	session['player_games_won'] = 0			#the current games won by player
	session['player_games_lost'] = 0		#the current games lost by player
	session['word_games_won'] = 0			#the current games won with that word
	session['word_games_losses'] = 0		#the current games losses with that word
	
	session['username'] = ""				#the session's username
	session['signed_in'] = False			#the session's signed in status
	session['token'] = ""					#the session's token
	
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
	#requires authentication for admin
    @wraps(f)
    def decorated(*args, **kwargs):
		
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
	
@app.route('/admin')
@requires_auth
def admin():
	return render_template('admin.html')

@app.route('/admin/words')
def admin_words_sort_functions():
	#use request arguments to get the sortBy and order data
	sortBy = request.args.get("sortby")
	order = request.args.get("order")
	logging.info(sortBy)
	logging.info(order)
	
	#get the list of words
	word_list = []
	
	#word, wins, losses
	#send a query
	query = game_list.query()
	words = query.get()
	
	#store the information in dictionary format
	for words in query:
		word_details = {}
		word_details['word'] = words.word.upper()		#key 1
		word_details['wins'] = words.wins				#key 2
		word_details['losses'] = words.losses			#key 3
		word_details['word_length'] = words.word_length	#key 4
		logging.info(word_list)
		
		word_list.append(word_details)
		
	if order == "desc":
		#by alphabet
		if sortBy == "alphabetical":
			#using the keys defined in player details, use it to sort according to requirement
			rows_by_word_desc = sorted(word_list, key=itemgetter('word'), reverse=True)
			logging.info(rows_by_word_desc)
			
			#make it an object to jsonify
			list = rows_by_word_desc
			return json.dumps(list)
		
		#by solved, aka wins
		elif sortBy == "solved":
			#using the keys defined in player details, use it to sort according to requirement
			rows_by_wins_desc = sorted(word_list, key=itemgetter('wins'), reverse=True)
			logging.info(rows_by_wins_desc)
			
			#make it an object to jsonify
			list = rows_by_wins_desc
			return json.dumps(list)
		
		#by length of word
		elif sortBy == "length":
			#using the keys defined in player details, use it to sort according to requirement
			rows_by_length_desc = sorted(word_list, key=itemgetter('word_length'), reverse=True)
			logging.info(rows_by_length_desc)
			
			#make it an object to jsonify
			list = rows_by_length_desc
			return json.dumps(list)
			
	elif order == "asc":
		#by alphabet
		if sortBy == "alphabetical":
			#using the keys defined in player details, use it to sort according to requirement
			rows_by_word_asc = sorted(word_list, key=itemgetter('word'))
			logging.info(rows_by_word_asc)
			
			#make it an object to jsonify
			list = rows_by_word_asc
			return json.dumps(list)
		
		#by solved, aka wins
		elif sortBy == "solved":
			#using the keys defined in player details, use it to sort according to requirement
			rows_by_wins_asc = sorted(word_list, key=itemgetter('wins'))
			logging.info(rows_by_wins_asc)
			
			#make it an object to jsonify
			list = rows_by_wins_asc
			return json.dumps(list)
		
		#by length of word
		elif sortBy == "length":
			#using the keys defined in player details, use it to sort according to requirement
			rows_by_length_asc = sorted(word_list, key=itemgetter('word_length'))
			logging.info(rows_by_length_asc)
			
			#make it an object to jsonify
			list = rows_by_length_asc
			return json.dumps(list)
		
	#returns nothing if all operations fail
	return '0'
	
@app.route('/admin/players')
def admin_player_sort_functions():
	#use request arguments to get the sortBy and order data
	sortBy = request.args.get("sortby")
	order = request.args.get("order")
	logging.info(sortBy)
	logging.info(order)
	
	#get the list of players
	player_list = []
	
	#send a query
	query = account_info.query()
	players = query.get()
	
	#store the information in dictionary format
	for players in query:
		player_details = {}
		player_details['name'] = players.username.upper()		#key 1
		player_details['games_won'] = players.games_won			#key 2
		player_details['games_lost'] = players.games_lost		#key 3
		player_details['games_played'] = players.games_played	#key 4
		player_details['games_created'] = players.games_created	#key 5
		logging.info(player_list)
		
		player_list.append(player_details)
	
	#depending on whether the order is ascending or descending.
	#follow up with the other settings of win/lose/alphabetical sort
	#by descending order
	if order == "desc":
		#by alphabet
		if sortBy == "alphabetical":
			#using the keys defined in player details, use it to sort according to requirement
			rows_by_name_desc = sorted(player_list, key=itemgetter('name'), reverse=True)
			logging.info(rows_by_name_desc)
			
			#make it an object to jsonify
			list = rows_by_name_desc
			return json.dumps(list)
		
		#by wins
		elif sortBy == "wins":
			#using the keys defined in player details, use it to sort according to requirement
			rows_by_wins_desc = sorted(player_list, key=itemgetter('games_won'), reverse=True)
			logging.info(rows_by_wins_desc)
			
			#make it an object to jsonify
			list = rows_by_wins_desc
			return json.dumps(list)
			
		#by losses
		elif sortBy == "losses":
			#using the keys defined in player details, use it to sort according to requirement
			rows_by_losses_desc = sorted(player_list, key=itemgetter('games_lost'), reverse=True)
			logging.info(rows_by_losses_desc)
			
			#make it an object to jsonify
			list = rows_by_losses_desc
			return json.dumps(list)
			
	#by ascending order
	elif order == "asc":
		#by alphabet
		if sortBy == "alphabetical":
			#using the keys defined in player details, use it to sort according to requirement
			rows_by_name_asc = sorted(player_list, key=itemgetter('name'))
			logging.info(rows_by_name_asc)
			
			#make it an object to jsonify
			list = rows_by_name_asc
			return json.dumps(list)
		
		#by wins
		elif sortBy == "wins":
			#using the keys defined in player details, use it to sort according to requirement
			rows_by_wins_asc = sorted(player_list, key=itemgetter('games_won'))
			logging.info(rows_by_wins_asc)
			
			#make it an object to jsonify
			list = rows_by_wins_asc
			return json.dumps(list)
		
		#by losses
		elif sortBy == "losses":
			#using the keys defined in player details, use it to sort according to requirement
			rows_by_losses_asc = sorted(player_list, key=itemgetter('games_lost'))
			logging.info(rows_by_losses_asc)
			
			#make it an object to jsonify
			list = rows_by_losses_asc
			return json.dumps(list)
			
	#returns nothing if all operations fail
	return '0'
	
#retrieve your game list using queries	
def get_games_available():
	#retrieve your game list using queries
	games_available = []
	
	query = game_list.query()
	games = query.get()
	
	for games in query:
		game = {}
		game['hint'] = games.hint
		game['word_length'] = games.word_length
		game['game_id'] = games.game_id
		#logging.info(game['hint'])
		#logging.info(game['word_length'])
		#logging.info(game['game_id'])
		games_available.append(game)
		
	return games_available
#default path
@app.route('/')
def home():
	if sign_in == True:
		games_available = get_games_available()
		#Renders the home page.
		return render_template('main.html', game_list = games_available, signed_in = session['signed_in'], sign_in_name = session['username'])
	else:
		totalSessionCount()
		
		#Renders the home page.
		return render_template('main.html', signed_in = False, sign_in_name = "")
		
#token path
@app.route('/token', methods = ['POST', 'GET'])
def token():
	global sign_in
	if request.method == 'POST':
		#generate a 15 characters long random generator
		f = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))
	
		#define the new kind
		new_entry = account_info()
		new_entry.signed_in = True
		new_entry.username = request.authorization.username
		new_entry.password = request.authorization.password
		new_entry.token = f
		new_entry.games_created = 0
		new_entry.games_played = 0
		new_entry.games_won = 0
		new_entry.games_lost = 0

		#creates if it doesn't exist
		#update if it exist
		new_entry.put()
		
		sign_in = True
		
		#assign a variable to the token
		response_dict = { 'token' : f }
		logging.info(response_dict)
		
		#pass it in to the client
		return json.dumps(response_dict)
	
	elif request.method == 'GET':
		
		#initialize the session here
		totalSessionCount()
		
		#get the details from client by request.headers
		tempstring = request.headers.get('Authorization')
		Basic_string, session['token'] = tempstring.split(' ', 1)
		session['username'], session['password'] = base64.standard_b64decode(session['token']).split(':')
		
		#query to the server using username and password
		query = account_info.query(account_info.username == session['username'])
		user = query.get()
		
		if user.password == session['password']:
			#load all the details related to the user
			session['games_created'] = user.games_created
			session['player_games_won'] = user.games_won
			session['player_games_lost'] = user.games_lost
			session['signed_in'] = True
			
			#then the account details
			acc_details = { 'token' : user.token, 'signed_in' : True }
			
			sign_in = True
			return json.dumps(acc_details)
			
		
	return '0'

#provide a word to be guessed and it's hint in this method
@app.route('/games', methods = ['GET', 'POST', 'DELETE'])
def post_word():
	if request.method == 'GET':
		#put this into another function and return it in json dump format
		all_games = get_games_available()
		
		return json.dumps(all_games)
		
	elif request.method == 'POST':
		#get the data from the js file
		data = request.data
		#check if the data is in json format
		logging.info(data)
		
		#if it is, then decode it to word and hint
		dict = json.loads(data)
		word = dict['word']
		hint = dict['hint']
		
		#check if the word and hint are decoded correctly
		logging.info(word)
		logging.info(hint)
		
		#generate a 15 characters long random generator
		f = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
		
		new_word = game_list()
		new_word.word = word				#based on the word given
		new_word.hint = hint				#based on the hint given
		new_word.word_length = len(word)	#based on the word set by player
		new_word.game_id = f				#based on the game id set by random generator
		new_word.wins = 0					#default the number of wins to 0
		new_word.losses = 0					#default the number of losses to 0
			
		logging.info(hint)
			
		new_word.put()
		
		#update the database for player
		query = account_info.query(account_info.username == session['username'])
		user = query.get()
		
		if user.username == session['username']:
			user.games_created += 1
			logging.info(user.games_created)
			user.put()
		
		game_word = {}
		game_word['word'] = word
		game_word['hint'] = hint
		game_word['word_length'] = len(word)
		game_word['game_id'] = f
			
		return json.dumps(game_word)

#play the game. Provide an ID beforehand
@app.route('/games/<game_id>', methods = ['GET'])
def play_game(game_id):
	if request.method == 'GET':
		target = game_id
		#the ID is already provided. Use that to get the specific information to it
		query = game_list.query(game_list.game_id == target)
		game = query.get()
		
		#query for player details too
		query2 = account_info.query()
		account = query2.get()
		
		
		if game.game_id == target:
			#transfer the game word over to the session
			session['game_answer'] = game.word.upper()		
			session['word_games_won'] = game.wins
			session['word_games_losses'] = game.losses
			
			#get the information of wins/losses of that account
			session['player_games_won'] = account.games_won
			session['player_games_lost'] = account.games_lost
			
			#set up those blanks
			blanks = ""
			for i in range(0, game.word_length):
				blanks += "_"
			session['current_word_state'] = blanks
		
			logging.info(game.hint)
			logging.info(game.word_length)
			game_info = {}
			game_info['hint'] = game.hint
			game_info['word_length'] = game.word_length
			game_info['game_id'] = game.game_id
			
			session['current_bad_guesses'] = -1
			
			return render_template('game.html', game_property = game_info)

@app.route('/games/<game_id>/check_letter', methods = ['POST'])
def check_letter(game_id):
	#this is a request body
	letter_guessed = json.loads(request.data)
	#Don't forget to check which tree you felled!
	logging.info(letter_guessed['guess'])
	
	#check that the game answer is correctly transferred over
	logging.info(session['game_answer'])
	
	#This is the answer in string format
	answer_in_string = list(session['game_answer'])
	
	#The length of the answer, numerically
	length_answer = len(session['game_answer'])
	
	#The current state of the game
	temp_word_state = list(session['current_word_state'])
	
	guess_Correctly = False
	
	#Let's begin the check
	for i in range(0, length_answer):
		#if the letter matches
		if answer_in_string[i] == letter_guessed['guess']:
			temp_word_state[i] = letter_guessed['guess']	#swap the blank out for the letter
			guess_Correctly = True
		elif(i == length_answer-1 and guess_Correctly == False): #in other words, he guessed wrongly
			session['current_bad_guesses'] += 1			#increment the bad guess count
	
	#join them altogether
	session['current_word_state'] = "".join(temp_word_state)
	
	#Don't forget to check which tree you felled!
	logging.info(session['current_word_state'])
	logging.info(session['game_answer'])
	
	if session['current_bad_guesses'] <= 7:
		#The game is ONGOING
		if(session['current_word_state'] != session['game_answer']):
			#the container meant for the current state of the game
			current_game_state = {}
			current_game_state.update({'game_state': "ONGOING"})
			current_game_state.update({'word_state': session['current_word_state']})
			current_game_state.update({'bad_guesses': session['current_bad_guesses']})
			the_current_state = json.dumps(current_game_state)
			return the_current_state
		
		#The game is WON
		else:
			
			#Update the status to win
			session['player_games_won'] += 1
			session['word_games_won'] += 1
			
			#the container meant for the current state of the game
			current_game_state = {}
			current_game_state.update({'games_won': session['player_games_won']})
			current_game_state.update({'game_state': "WIN"})
			current_game_state.update({'word_state': session['current_word_state']})
			the_current_state = json.dumps(current_game_state)
			
			#update the word number of wins
			target = game_id
			query = game_list.query(game_list.game_id == target)
			game = query.get()
			
			if game.game_id == target:
				#update the word and player's status
				game.wins = session['word_games_won']
				logging.info(game.wins)
				game.put()
			
			#update the account's statistics database
			query2 = account_info.query(account_info.username == session['username'])
			user = query2.get()
			
			#this is the correct user
			if user.username == session['username']:
				#update the player's number of wins
				user.games_won = session['player_games_won']
				logging.info(user.games_won)
				user.put()
			
			return the_current_state
	
	#he loses the game if any of those conditions above doesn't match
	if session['current_bad_guesses'] >= 8:
		
		#update the number of losses
		session['player_games_lost'] += 1
		session['word_games_losses'] += 1
		
		#Update the status to lose
		#the container meant for the current state of the game
		current_game_state = {}
		current_game_state.update({'games_lost': session['player_games_lost']})
		current_game_state.update({'game_state': "LOSE"})
		current_game_state.update({'word_state': session['current_word_state']})
		current_game_state.update({'answer': session['game_answer']})
		the_current_state = json.dumps(current_game_state)
		
		
		#update the word statistics database
		target = game_id
		query = game_list.query(game_list.game_id == target)
		game = query.get()
		
		if game.game_id == target:
			#update the word and player's status
			game.losses = session['word_games_losses']
			logging.info(game.losses)
			game.put()
		
		#update the account's statistics database
		query2 = account_info.query(account_info.username == session['username'])
		user = query2.get()
		
		#this is the correct user
		if user.username == session['username']:
			#update the player's number of wins
			user.games_lost = session['player_games_lost']
			logging.info(user.games_lost)
			user.put()
		
		return the_current_state