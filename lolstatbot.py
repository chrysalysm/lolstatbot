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
import os # for relative pathing
import string # for string manipulation
# from routes import API_ROUTES

class API_ROUTES:
	# summoner-v1.4 - get summoner id data
	summoner_url = 'https://{region}.api.pvp.net/api/lol/{region}/v1.4/summoner/by-name/{summonername}?api_key={key}'

	# summoner-v1.4 - summoner mastery data
	summonermastery_url = 'https://{region}.api.pvp.net/api/lol/{region}/v1.4/summoner/{summonerid}/masteries?api_key={key}'

	# league-v2.5 - summoner league data
	summonerleague_url = 'https://{region}.api.pvp.net/api/lol/{region}/v2.5/league/by-summoner/{summonerid}/entry?api_key={key}'
	
	# lol-static-data-v1.2 - static champion data
	championstaticdata_url = 'https://global.api.pvp.net/api/lol/static-data/{region}/v1.2/champion/{championid}?champData=all&api_key={key}'
	
	# lol-static-data-v1.2 - static rune data
	runestaticdata_url = 'https://global.api.pvp.net/api/lol/static-data/{region}/v1.2/rune/{runeid}?runeData=all&api_key={key}'

	# lol-static-data-v1.2 - static mastery data
	masterystaticdata_url = 'https://global.api.pvp.net/api/lol/static-data/{region}/v1.2/mastery/{masteryid}?masteryData=all&api_key={key}'

	# lol-static-data-v1.2 - static spell data
	spellstaticdata_url = 'https://global.api.pvp.net/api/lol/static-data/{region}/v1.2/summoner-spell/{spellid}?api_key={key}'

	# current-game-v1.0 - current game data
	current_url = 'https://{region}.api.pvp.net/observer-mode/rest/consumer/getSpectatorGameInfo/{region_upper}1/{summonerid}?api_key={key}'
	
	# game-v1.3 - historic game data
	last_url = 'https://{region}.api.pvp.net/api/lol/{region}/v1.3/game/by-summoner/{summonerid}/recent?api_key={key}'
	
	# op.gg
	opgg_url = 'http://{region}.op.gg/summoner/userName={summonername}'
	opgg_masteries_url = 'http://{region}.op.gg/summoner/mastery/userName={summonername}'
	opgg_runes_url = 'http://{region}.op.gg/summoner/rune/userName={summonername}'
	opgg_matches_url = 'http://{region}.op.gg/summoner/matches/userName={summonername}'
	opgg_leagues_url = 'http://{region}.op.gg/summoner/league/userName={summonername}'
	opgg_champions_url = 'http://{region}.op.gg/summoner/champions/userName={summonername}'

	# LoLNexus
	lolnexus_url = 'http://www.lolnexus.com/{region}/search?name={summonername}&server={region}'
	
	# LoLKing
	lolking_url = 'http://www.lolking.net/summoner/{region}/{summonerid}'
	
	# LoLSkill
	lolskill_url = 'http://www.lolskill.net/summoner/{region}/{summonername}'

# ====== READ CONFIG ======
Config = ConfigParser.ConfigParser()
Config.read(os.path.dirname(os.path.abspath(__file__)) + '/config.ini')

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
summonerName = summonerName.replace(" ", "")
region = ConfigSectionMap('settings')['region']

summoner_url = API_ROUTES.summoner_url.format(region=region, summonername=summonerName, key=api_key)

# Initial Data Load // Get Summoner ID and Level
summonerName_dict = requests.get(summoner_url).json()
summonerID = str(summonerName_dict[summonerName]['id'])
summonerLevel = str(summonerName_dict[summonerName]['summonerLevel'])

# ====== RIOT API FUNCTIONS ======

def about(ircname):
	return 'Hello ' + ircname + '! I am a League of Legends statistics chat bot. My creator is blenderben [ https://github.com/blenderben/LoLStatBot ].'\
	+ ' I am currently assigned to summoner ' + summonerName.upper() + ' [ID:' + getSummonerID() + '].'

def getCommands():
	return 'Available commands: ['\
	+ ' !about, !summoner, !league, !last, !current, !runes, !mastery, !opgg, !lolnexus, !lolking, !lolskill ]'

def getSummonerInfo():
	return summonerName.upper() + ' is summoner level ' + getSummonerLevel() + ', playing in Region: ' + region.upper() + ' // ' + opgg('')

def opgg(details):
	if details == 'runes':
		return API_ROUTES.opgg_runes_url.format(region=region, summonername=summonerName)
	elif details == 'masteries':
		return API_ROUTES.opgg_masteries_url.format(region=region, summonername=summonerName)
	elif details == 'matches':
		return API_ROUTES.opgg_matches_url.format(region=region, summonername=summonerName)
	elif details == 'leagues':
		return API_ROUTES.opgg_leagues_url.format(region=region, summonername=summonerName)
	elif details == 'champions':
		return API_ROUTES.opgg_champions_url.format(region=region, summonername=summonerName)
	else:
		return API_ROUTES.opgg_url.format(region=region, summonername=summonerName)

def lolnexus():
	return API_ROUTES.lolnexus_url.format(region=region, summonername=summonerName)

def lolking(details):
	if details == 'runes':
		return API_ROUTES.lolking_url.format(region=region, summonerid=summonerID) + '#runes'
	elif details == 'masteries':
		return API_ROUTES.lolking_url.format(region=region, summonerid=summonerID) + '#masteries'
	elif details == 'matches':
		return API_ROUTES.lolking_url.format(region=region, summonerid=summonerID) + '#matches'
	elif details == 'rankedstats':
		return API_ROUTES.lolking_url.format(region=region, summonerid=summonerID) + '#ranked-stats'
	elif details == 'leagues':
		return API_ROUTES.lolking_url.format(region=region, summonerid=summonerID) + '#leagues'
	else:
		return API_ROUTES.lolking_url.format(region=region, summonerid=summonerID)

def lolskill(details):
	if details == 'runes':
		return API_ROUTES.lolskill_url.format(region=region.upper(), summonername=summonerName) + '/runes'
	elif details == 'masteries':
		return API_ROUTES.lolskill_url.format(region=region.upper(), summonername=summonerName) + '/masteries'
	elif details == 'matches':
		return API_ROUTES.lolskill_url.format(region=region.upper(), summonername=summonerName) + '/matches'
	elif details == 'stats':
		return API_ROUTES.lolskill_url.format(region=region.upper(), summonername=summonerName) + '/stats'
	elif details == 'champions':
		return API_ROUTES.lolskill_url.format(region=region.upper(), summonername=summonerName) + '/champions'
	else:
		return API_ROUTES.lolskill_url.format(region=region.upper(), summonername=summonerName)


def getTeamColor(teamid):
	if teamid == 100:
		return 'Blue Team'
	elif teamid == 200:
		return 'Purple Team'
	else:
		return 'No Team'

def getWinLoss(win):
	if win == True:
		return 'WON'
	elif win == False:
		return 'LOST'
	else:
		return 'TIED'

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
		return str(time) + ' seconds'

def getKDA(kills, deaths, assists):
	if deaths < 1:
		return 'PERFECT'
	else:
		kda = float(kills) + float(assists) /  (float(deaths))
		kda = round(kda, 2)
		return str(kda) + ':1'

def getChampionbyID(championid):
	tempDict = requests.get(API_ROUTES.championstaticdata_url.format(region=region, championid=int(championid), key=api_key)).json()
	name = tempDict['name'] + " " + tempDict['title']
	return name

def getSpellbyID(spellid):
	tempDict = requests.get(API_ROUTES.spellstaticdata_url.format(region=region, spellid=int(spellid), key=api_key)).json()
	spellName = tempDict['name']
	return spellName

# Refresh / Get Summoner ID
def getSummonerID():
	global summonerID
	try:
		tempDict = requests.get(summoner_url).json()
		summonerID = str(tempDict[summonerName]['id'])
		return summonerID
	except:
		print 'Riot API Down'
		return 1

# Refresh / Get Summoner Level
def getSummonerLevel():
	global summonerLevel
	tempDict = requests.get(summoner_url).json()
	summonerLevel = str(tempDict[summonerName]['summonerLevel'])
	return summonerLevel

def getWinRatio(win, loss):
	total = float(win) + float(loss)
	ratio = win / total
	ratioPercent = round(ratio * 100, 1)
	return str(ratioPercent) + '%'

def getStats():
	# Function to eventually get statistics, avg kills, etc, for now, output Stats page from Lolskill
	return lolskill('stats')

def getSummonerMastery():
	tempDict = requests.get(API_ROUTES.summonermastery_url.format(region=region, summonerid=summonerID, key=api_key)).json()
	i = 0
	masteryIDList = []
	masteryRank = []
	for pages in tempDict[summonerID]['pages']:
		if bool(pages.get('current')) == True:
			pageName = tempDict[summonerID]['pages'][i]['name']
			for mastery in tempDict[summonerID]['pages'][i]['masteries']:
				masteryIDList.append(mastery.get('id'))
				masteryRank.append(mastery.get('rank'))
		else:
			i += 1

	return getCurrentMastery(masteryIDList, masteryRank) + ' // Mastery Name: ' + pageName

def getLeagueInfo():
	try:
		tempDict = requests.get(API_ROUTES.summonerleague_url.format(region=region, summonerid=summonerID, key=api_key)).json()
		LEAGUE_TIER = string.capwords(tempDict[summonerID][0]['tier'])
		LEAGUE_QUEUE = tempDict[summonerID][0]['queue'].replace('_', ' ')
		LEAGUE_DIVISION = tempDict[summonerID][0]['entries'][0]['division']
		LEAGUE_WINS = tempDict[summonerID][0]['entries'][0]['wins']
		LEAGUE_LOSSES = tempDict[summonerID][0]['entries'][0]['losses']
		LEAGUE_POINTS = tempDict[summonerID][0]['entries'][0]['leaguePoints']
		# LEAGUE_ISVETERAN = tempDict[summonerID][0]['entries'][0]['isHotStreak']
		# LEAGUE_ISHOTSTREAK = tempDict[summonerID][0]['entries'][0]['isVeteran']
		# LEAGUE_ISFRESHBLOOD = tempDict[summonerID][0]['entries'][0]['isFreshBlood']
		# LEAGUE_ISINACTIVE = tempDict[summonerID][0]['entries'][0]['isInactive']

		return summonerName.upper() + ' is ' + LEAGUE_TIER + ' ' + LEAGUE_DIVISION + ' in ' + LEAGUE_QUEUE\
		+ ' // ' + str(LEAGUE_WINS) + 'W / ' + str(LEAGUE_LOSSES) + 'L (Win Ratio ' + getWinRatio(LEAGUE_WINS, LEAGUE_LOSSES) + ')'\
		+ ' // LP: ' + str(LEAGUE_POINTS)\
		+ ' // ' + lolking('leagues')
	except:
		return 'Summoner ' + summonerName.upper() + ' has not played any Ranked Solo 5x5 matches'\
		+ ' // ' + lolking('leagues')

# Get Current Match Stats
def getCurrent(details):
	try:
		current_api_url = API_ROUTES.current_url.format(region=region, region_upper=region.upper(), summonerid=summonerID, key=api_key)
		tempDict = requests.get(current_api_url).json()
		
		CURRENT_GAMEMODE = tempDict['gameMode']
		CURRENT_GAMELENGTH = tempDict['gameLength']
		CURRENT_GAMETYPE = tempDict['gameType'].replace('_', ' ')

		CURRENT_TIME = calendar.timegm(time.gmtime())
		CURRENT_EPOCHTIME = tempDict['gameStartTime'] / 1000

		if CURRENT_EPOCHTIME <= 0:
			CURRENT_TIMEDIFF = 0
		else:
			CURRENT_TIMEDIFF = CURRENT_TIME - CURRENT_EPOCHTIME
			if CURRENT_TIMEDIFF < 0:
				CURRENT_TIMEDIFF = 0

		runeIDList = []
		runeCount = []
		masteryIDList = []
		masteryRank = []
		i = 0
		for participant in tempDict['participants']:
			if int(summonerID) == int(participant.get('summonerId')):
				CURRENT_TEAM = participant.get('teamId')
				CURRENT_CHAMPION = participant.get('championId')
				CURRENT_SPELL1 = participant.get('spell1Id')
				CURRENT_SPELL2 = participant.get('spell2Id')
				for rune in tempDict['participants'][i]['runes']:
					runeIDList.append(rune.get('runeId'))
					runeCount.append(rune.get('count'))
				for mastery in tempDict['participants'][i]['masteries']:
					masteryIDList.append(mastery.get('masteryId'))
					masteryRank.append(mastery.get('rank'))
			else:
				i += 1

		runeCountOutput = ''
		runeBonusOutput = ''
		for x in range(len(runeIDList)):
			runeCountOutput += ' [' + getCurrentRuneTotal(runeIDList[x], runeCount[x]) + '] '
			runeBonusOutput += ' [' + getCurrentRuneBonusTotal(runeIDList[x], runeCount[x]) + '] '
		
		masteryOutput = getCurrentMastery(masteryIDList, masteryRank)

		if details == 'runes':
			return 'Current Runes: ' + runeCountOutput\
			+ ' // Rune Bonuses: ' + runeBonusOutput\
			+ ' // ' + lolskill('runes')
		elif details == 'masteries':
			return 'Current Mastery Distribution: ' + masteryOutput\
			+ ' // ' + lolskill('masteries')
		else:
			return summonerName.upper()\
			+ ' is currently playing ' + CURRENT_GAMEMODE + ' ' + CURRENT_GAMETYPE\
			+ ' with ' + getChampionbyID(CURRENT_CHAMPION)\
			+ ' on the ' + getTeamColor(CURRENT_TEAM)\
			+ ' // Elapsed Time: ' +  getTimePlayed(CURRENT_TIMEDIFF)\
			+ ' // Spells Chosen: ' + getSpellbyID(CURRENT_SPELL1) + ' & ' + getSpellbyID(CURRENT_SPELL2)\
			+ ' // Mastery Distribution: ' + masteryOutput\
			+ ' // Rune Bonuses: ' + runeBonusOutput\
			+ ' // ' + lolnexus()

	except:
		if details == 'runes':
			return 'Summoner ' + summonerName.upper() + ' needs to currently be in a game for current Rune data to display'\
			+ ' // ' + lolking('runes')
		elif details == 'masteries':
			return 'Current Mastery Distribution: ' + getSummonerMastery() + ' // ' + lolskill('masteries')
		else:
			return 'The summoner ' + summonerName.upper() + ' is not currently in a game.'

def getCurrentMastery(masteryidlist, masteryrank):
	offense = 0
	defense = 0
	utility = 0
	for x in range(len(masteryidlist)):
		masteryID = masteryidlist[x]
		tempDict = requests.get(API_ROUTES.masterystaticdata_url.format(region=region, masteryid=masteryID, key=api_key)).json()
		masteryTree = tempDict['masteryTree']
		ranks = int(masteryrank[x])

		if masteryTree == 'Offense':
			offense += ranks
		elif masteryTree == 'Defense':
			defense += ranks
		else: 
			utility += ranks

	return '(' + str(offense) + '/' + str(defense) + '/' + str(utility) + ')'

def getCurrentRuneTotal(runeid, count):
	tempDict = requests.get(API_ROUTES.runestaticdata_url.format(region=region, runeid=runeid, key=api_key)).json()
	runeName = tempDict['name']
	return str(count) + 'x ' + runeName

def getCurrentRuneBonusTotal(runeid, count):
	tempDict = requests.get(API_ROUTES.runestaticdata_url.format(region=region, runeid=runeid, key=api_key)).json()
	runeBonus = tempDict['description']
	try:
		runeBonus.split('/')[1]
	except IndexError:
		# Single Bonus
		value = runeBonus.split()[0]
		value = value.replace('+', '').replace('%', '').replace('-', '')
		valueCount = float(value) * float(count)
		valueCount = round(valueCount, 2)
		description = tempDict['description'].split(' (', 1)[0]
		description = string.capwords(description)
		description = description.replace(value, str(valueCount))
		return description
	else:
		# Hybrid Bonus
		value = runeBonus.split()[0]
		value = value.replace('+', '').replace('%', '').replace('-', '')
		valueCount = float(value) * float(count)
		valueCount = round(valueCount, 2)
		firstDescription = runeBonus.split('/')[0].strip()
		firstDescription = firstDescription.split(' (', 1)[0]
		firstDescription = string.capwords(firstDescription)
		firstDescription = firstDescription.replace(value, str(valueCount))

		value = runeBonus.split('/')[1].strip()
		if value.split()[1] == 'sec.':
			return firstDescription + ' / 5 Sec.'
		else:
			value = value.split()[0]
			value = value.replace('+', '').replace('%', '').replace('-', '')
			valueCount = float(value) * float(count)
			valueCount = round(valueCount, 2)
			secondDescription = runeBonus.split('/')[1].strip()
			secondDescription = secondDescription.split(' (', 1)[0]
			secondDescription = string.capwords(secondDescription)
			secondDescription = secondDescription.replace(value, str(valueCount))
			return firstDescription + ' / ' + secondDescription

# Get Last Match Stats
def getLast():
	tempDict = requests.get(API_ROUTES.last_url.format(region=region, summonerid=summonerID, key=api_key)).json()

	LAST_GAMEID = tempDict['games'][0]['gameId']
	# LAST_GAMEMODE = tempDict['games'][0]['gameMode']
	LAST_SUBTYPE = tempDict['games'][0]['subType'].replace('_', ' ')
	LAST_GAMETYPE = tempDict['games'][0]['gameType'].replace('_GAME', '')
	LAST_TIMEPLAYED = tempDict['games'][0]['stats']['timePlayed']
	LAST_WIN = tempDict['games'][0]['stats']['win']
	LAST_GOLDSPENT = tempDict['games'][0]['stats']['goldSpent']
	LAST_GOLDEARNED = tempDict['games'][0]['stats']['goldEarned']

	LAST_CHAMPION_ID = str(tempDict['games'][0]['championId'])
	LAST_IPEARNED = str(tempDict['games'][0]['ipEarned'])
	LAST_LEVEL = str(tempDict['games'][0]['stats']['level'])

	LAST_SPELL1 = tempDict['games'][0]['spell1']
	LAST_SPELL2 = tempDict['games'][0]['spell2']
	
	LAST_CHAMPIONSKILLED = str(tempDict['games'][0]['stats'].get('championsKilled', 0))
	LAST_NUMDEATHS = str(tempDict['games'][0]['stats'].get('numDeaths' , 0))
	LAST_ASSISTS = str(tempDict['games'][0]['stats'].get('assists', 0))

	LAST_TOTALDAMAGECHAMPIONS = str(tempDict['games'][0]['stats']['totalDamageDealtToChampions'])
	LAST_MINIONSKILLED = str(tempDict['games'][0]['stats']['minionsKilled'])
	LAST_WARDSPLACED = str(tempDict['games'][0]['stats'].get('wardPlaced', 0))

	output = summonerName.upper() + ' ' + getWinLoss(LAST_WIN)\
	+ ' the last ' + LAST_GAMETYPE + ' ' + LAST_SUBTYPE\
	+ ' GAME using ' + getChampionbyID(LAST_CHAMPION_ID)\
	+ ' // The game took ' + getTimePlayed(LAST_TIMEPLAYED)\
	+ ' // ' + getKDA(LAST_CHAMPIONSKILLED, LAST_NUMDEATHS, LAST_ASSISTS) + ' KDA (' + LAST_CHAMPIONSKILLED + '/' + LAST_NUMDEATHS + '/' + LAST_ASSISTS + ')'\
	+ ' // ' + getSpellbyID(LAST_SPELL1) + ' & ' + getSpellbyID(LAST_SPELL2) + ' spells were chosen'\
	+ ' // ' + LAST_TOTALDAMAGECHAMPIONS + ' damage was dealt to champions'\
	+ ' // ' + LAST_MINIONSKILLED + ' minions were killed'\
	+ ' // ' + LAST_WARDSPLACED + ' wards were placed'\
	+ ' // Spent ' + str(round(float(LAST_GOLDSPENT) / float(LAST_GOLDEARNED)*100, 1)) + '% of Gold earned [' + str(LAST_GOLDSPENT) + '/' + str(LAST_GOLDEARNED) + ']'\
	+ ' // ' + LAST_IPEARNED + ' IP was earned'
	# add Official League Match history here
	return output

# ====== IRC FUNCTIONS ======

# Extract Nickname
def getNick(data):
	nick = data.split('!')[0]
	nick = nick.replace(':', ' ')
	nick = nick.replace(' ', '')
	nick = nick.strip(' \t\n\r')
	return nick

def getMessage(data):
	if data.find('PRIVMSG'):
		try:
			message = data.split(channel, 1)[1][2:]
			return message
		except IndexError:
			return 'Index Error'
		except:
			return 'No message'
	else:
		return 'Not a message'

# ====== TIMER FUNCTIONS ======

def printit():
	threading.Timer(60.0, printit).start()
	print "Hello World"

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

printit()

# Main Program Loop
while True:

	ircdata = irc.recv(4096) # gets output from IRC server
	ircuser = ircdata.split(':')[1]
	ircuser = ircuser.split('!')[0] # determines the sender of the messages

	# Check messages for any banned words against banned.txt list
	f = open(os.path.dirname(os.path.abspath(__file__)) + '/banned.txt', 'r')
	banned = f.readlines()
	message = getMessage(ircdata).lower().strip(' \t\n\r')
	for i in range(len(banned)):
		if message.find(banned[i].strip(' \t\n\r')) != -1:
			irc.send('PRIVMSG ' + channel + ' :' + getNick(ircdata) + ', banned words are not allowed.  A timeout has been issued.' + '\r\n')
			# irc.send('PRIVMSG ' + channel + ' :\/timeout ' + getNick(ircdata) + ' 5\r\n')
			break
		else:
			pass

	print 'DEBUG: ' + ircdata.strip(' \t\n\r')
	print 'USER: ' + getNick(ircdata).strip(' \t\n\r')
	print 'MESSAGE: ' + getMessage(ircdata).strip(' \t\n\r')
	print '======================='
	# About
	if ircdata.find(':!about') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + about(getNick(ircdata)) + '\r\n')

	# Commands
	if ircdata.find(':!commands') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + getCommands() + '\r\n')

	# Last
	if ircdata.find(':!last') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + getLast() + '\r\n')

	# Current
	if ircdata.find(':!current') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + getCurrent('games') + '\r\n')

	# Current Runes
	if ircdata.find(':!runes') != -1 or ircdata.find(':!rune') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + getCurrent('runes') + '\r\n')

	# Current Mastery
	if ircdata.find(':!mastery') != -1 or ircdata.find(':!masteries') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + getCurrent('masteries') + '\r\n')

	# Basic Summoner Data
	if ircdata.find(':!summoner') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + getSummonerInfo() + '\r\n')

	# Seaonal League Rank Data
	if ircdata.find(':!league') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + getLeagueInfo() + '\r\n')

	# Stats
	if ircdata.find(':!stats') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + getStats() + '\r\n')

	# Return op.gg
	if ircdata.find(':!opgg') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + opgg('') + '\r\n')

	# Return lolnexus
	if ircdata.find(':!lolnexus') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + lolnexus() + '\r\n')

	# Return lolking
	if ircdata.find(':!lolking') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + lolking('') + '\r\n')

	# Return lolskill
	if ircdata.find(':!lolskill') != -1:
		irc.send('PRIVMSG ' + channel + ' :' + lolskill('') + '\r\n')

	# Keep Alive
	if ircdata.find('PING') != -1:
		irc.send('PONG ' + ircdata.split()[1] + '\r\n')
