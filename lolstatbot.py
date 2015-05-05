# Leauge of Legends Statistics Chat Bot
# A chat bot written in Python that provides match statistics right to your Twitch chat.
# 2015 Benjamin Chu - https://github.com/blenderben

import socket # imports module allowing connection to IRC
import threading # imports module allowing timing functions
import requests # imports module allowing requests
import json
import time
import calendar # imports module allowing epoch time
import ConfigParser # imports module allowing reading of .ini files
# from routes import API_ROUTES

class API_ROUTES:
	# summoner-v1.4 - https://developer.riotgames.com/api/methods#!/983
	summoner_url = 'https://{region}.api.pvp.net/api/lol/{region}/v1.4/summoner/by-name/{name}?api_key={key}'
	# lol-static-data-v1.2
	lolstaticdata_url = 'https://global.api.pvp.net/api/lol/static-data/{region}/v1.2/champion/{num}?api_key={key}'
	# current-game-v1.0
	current_url = 'https://{region}.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/{region_upper}1/{summonerid}?api_key={key}'
	# game-v1.3
	last_url = 'https://{region}.api.pvp.net/api/lol/{region}/v1.3/game/by-summoner/{summonerid}/recent?api_key={key}'
	# op.gg
	opgg_url = 'http://{region}.op.gg/summoner/userName={name}'
	# LoLNexus
	lolnexus_url = 'http://www.lolnexus.com/{region}/search?name={name}&server={region}'

# ====== READ CONFIG ======
Config = ConfigParser.ConfigParser()
Config.read('config.ini')
def ConfigSectionMap(section):
    temp_dict = {}
    options = Config.options(section)
    for option in options:
        try:
            temp_dict[option] = Config.get(section, option)
            if temp_dict[option] == -1:
                DebugPrint('skip: %s' % option)
        except:
            print('exception on %s!' % option)
            temp_dict[option] = None
    return temp_dict
    del temp_dict

# ====== CONNECTION INFO ======

# Set variables for connection
botOwner = ConfigSectionMap('settings')['botowner']
nick = ConfigSectionMap('settings')['nick']
channel = '#' + ConfigSectionMap('settings')['channel']
server = ConfigSectionMap('settings')['server']
port = int(ConfigSectionMap('settings')['port'])
password = ConfigSectionMap('settings')['oauth']

# ====== RIOT API PRELIM DATA ======
api_key = ConfigSectionMap('settings')['api']

# Riot API Information
summonerName = ConfigSectionMap('settings')['summonername'].lower()
region = ConfigSectionMap('settings')['region']

#api_url = 'https://' + region + '.api.pvp.net/api/lol/' + region
summoner_url = API_ROUTES.summoner_url.format(region=region, name=summonerName, key=api_key)

# Initial Data Load // Get Summoner ID and Level
summonerName_dict = requests.get(summoner_url).json()
summonerID = str(summonerName_dict[summonerName]['id'])
summonerLevel = str(summonerName_dict[summonerName]['summonerLevel'])

# ====== RIOT API FUNCTIONS ======

def getWinLoss(win):
	if win == True:
		return 'WON'

	if win == False:
		return 'LOST'

def getEpochTime(time):
	return 'test'


def getTimePlayed(time):
	if time > 3600:
		hours = time / 3600
		minutes = time % 3600 / 60
		seconds = time % 3600 % 60
		if hours > 1:
			return str(hours) + ' hours & ' + str(minutes) + ' minutes & ' + str(seconds) + ' seconds'
		else:
			return str(hours) + ' hour & ' + str(minutes) + ' minutes & ' + str(seconds) + ' seconds'
	elif time > 60:
		minutes = time / 60
		seconds = time % 60
		return str(minutes) + ' minutes & ' + str(seconds) + ' seconds'
	else:
		return str(seconds) + ' seconds'


def getChampionbyID(idNum):
	tempDict = requests.get(API_ROUTES.lolstaticdata_url.format(region=region, num=idNum, key=api_key)).json()
	name = tempDict['name'] + " " + tempDict['title']
	return name

# Refresh / Get Summoner ID
def getSummonerID():
	global summonerID
	tempDict = requests.get(summoner_url).json()
	summonerID = str(tempDict[summonerName]['id'])
	return summonerID

# Refresh / Get Summoner Level
def getSummonerLevel():
	global summonerLevel
	tempDict = requests.get(summoner_url).json()
	summonerLevel = str(tempDict[summonerName]['summonerLevel'])
	return summonerLevel

def getSummonerInfo():
	return summonerName.upper() + ' is summoner level ' + getSummonerLevel() + ', playing in Region: ' + region.upper() + ' - ' + opgg()

def about():
	return 'I am a League of Legends Statistics Bot. My creator is blenderben [https://github.com/blenderben/LoLStatBot]. I am currently assigned to summoner ' + summonerName.upper() + ' [ID:' + getSummonerID() + '].'

def opgg():
	return API_ROUTES.opgg_url.format(region=region, name=summonerName)
	#return 'http://' + region + '.op.gg/summoner/userName=' + summonerName

def lolnexus():
	return API_ROUTES.lolnexus_url.format(region=region, name=summonerName)

# Get Current Match Stats
def getCurrent():
	#try:
		current_api_url = API_ROUTES.current_url.format(region=region, region_upper=region.upper(), summonerid=summonerID, key=api_key)
		tempDict = requests.get(current_api_url).json()
		CURRENT_GAMEMODE = tempDict['gameMode']
		CURRENT_GAMELENGTH = tempDict['gameLength']
		return CURRENT_GAMEMODE + ' // ' + getTimePlayed(int(CURRENT_GAMELENGTH))
		#return CURRENT_GAMEMODE + ' // ' + getTimePlayed(int(CURRENT_GAMELENGTH)) + ' // Game was created: ' + getTimePlayed(int(CURRENT_GAMESTARTTIME)) + ' ago.'
		#tempDict['gameMode'] # seconds
		#tempDict['gameStartTime'] # epoch time

		# for loop through participants to find matching summonerName, record num, pull teamId, championId, runes

		# Data to fetch from API
		# gameLength
		# gameMode
		# gameStartTime

		# participants
		# runes

		# teamId
		# summonerName
		# championId

	#except:
	#	return 'The summoner ' + summonerName.upper() + ' is not currently in a game.'

# Get Last Match Stats
def getLast(): # last_url = 'https://{region}.api.pvp.net/api/lol/{region}/v1.3/game/by-summoner/{summonerid}/recent?api_key={key}'
	tempDict = requests.get(API_ROUTES.last_url.format(region=region, summonerid=summonerID, key=api_key)).json()

	LAST_GAMEID = tempDict['games'][0]['gameId']
	LAST_GAMEMODE = tempDict['games'][0]['gameMode'] 
	LAST_TIMEPLAYED = tempDict['games'][0]['stats']['timePlayed']
	LAST_WIN = tempDict['games'][0]['stats']['win']
	LAST_GOLDSPENT = tempDict['games'][0]['stats']['goldSpent']
	LAST_GOLDEARNED = tempDict['games'][0]['stats']['goldEarned']

	LAST_CHAMPION_ID = str(tempDict['games'][0]['championId'])
	LAST_IPEARNED = str(tempDict['games'][0]['ipEarned'])
	LAST_LEVEL = str(tempDict['games'][0]['stats']['level'])
	LAST_CHAMPIONSKILLED = str(tempDict['games'][0]['stats']['championsKilled'])
	LAST_NUMDEATHS = str(tempDict['games'][0]['stats']['numDeaths'])
	LAST_ASSISTS = str(tempDict['games'][0]['stats']['assists'])
	LAST_TOTALDAMAGECHAMPIONS = str(tempDict['games'][0]['stats']['totalDamageDealtToChampions'])
	LAST_MINIONSKILLED = str(tempDict['games'][0]['stats']['minionsKilled'])
	LAST_WARDSPLACED = str(tempDict['games'][0]['stats'].get('wardPlaced', 0))

	output = 'The last game took ' + getTimePlayed(LAST_TIMEPLAYED) + ' // '\
	+ summonerName.upper() + ' ' + getWinLoss(LAST_WIN) + ' the last ' + LAST_GAMEMODE + ' game using ' + getChampionbyID(LAST_CHAMPION_ID) + ' // '\
	+ str(round(float(LAST_CHAMPIONSKILLED) + float(LAST_ASSISTS) / float(LAST_NUMDEATHS), 2)) + ':1 KDA (' + LAST_CHAMPIONSKILLED + '/' + LAST_NUMDEATHS + '/' + LAST_ASSISTS + ') // ' \
	+ LAST_TOTALDAMAGECHAMPIONS + ' damage was dealt to champions // '\
	+ LAST_MINIONSKILLED + ' minions were killed // '\
	+ LAST_WARDSPLACED + ' wards were placed // '\
	+ 'Spent ' + str(round(float(LAST_GOLDSPENT) / float(LAST_GOLDEARNED)*100, 1)) + '% of Gold earned [' + str(LAST_GOLDSPENT) + '/' + str(LAST_GOLDEARNED) + '] // '\
	+ LAST_IPEARNED + ' IP was earned'
	return output

# ====== IRC FUNCTIONS ======

# Get IRC recv nick

# ===============================

# queue = 13 #sets variable for anti-spam queue functionality
# Connect to server
print '\nConnecting to: ' + server + ' over port ' + str(port)
irc = socket.socket()
irc.connect((server, port))

# Send variables for connection to Twitch chat
irc.send('PASS ' + password + '\r\n')
irc.send('USER ' + nick + ' 0 * :' + botOwner + '\r\n')
irc.send('NICK ' + nick + '\r\n')
irc.send('JOIN ' + channel + '\r\n')

# Main Program Loop
while True:
	ircdata = irc.recv(1204) #gets output from IRC server
	ircuser = ircdata.split(':')[1]
	ircuser = ircuser.split('!')[0] #determines the sender of the messages
	print 'DEBUG: ' + ircdata
	print 'User: ' + ircuser

	# About
	if ircdata.find(':!about') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + about() + '\r\n')


	# Last
	if ircdata.find(':!last') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + getLast() + '\r\n')

	# Current
	if ircdata.find(':!current') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + getCurrent() + '\r\n')


	# Summoner Data
	if ircdata.find(':!summoner') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + getSummonerInfo() + '\r\n')


	# Keep Alive
	if ircdata.find('PING') != -1:
		irc.send(ircdata.replace('PING', 'PONG')) #responds to PINGS from the server