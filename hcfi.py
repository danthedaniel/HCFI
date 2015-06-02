from bs4 import BeautifulSoup
import requests
import arrow
import re

from requests.exceptions import HTTPError

class Faction:
    def __init__(self, name):
        self.name = name
        self.data = {}
        self.players = []

    def __str__(self):
        return self.name

    def __len__(self):
        try:
            return self.data['Members']
        except AttributeError:
            return None

class Player:
    def __init__(self, username):
        self.username = username
        self.data = {}

    def __str__(self):
        return self.username

class HCFI:
    def __init__(self):
        self.highlifesTimezone = 'US/Central' # He's 2 cool 4 EST
        self.globalTimeout = 60 # 60 seconds
        self.headers = {'User-Agent': 'HCFactions Python Interface v0.1'}

        self.cacheTimeouts = {}
        self.factionCache  = {}
        self.playerCache   = {}

        regfc = r'^(Power|Members|Dead Members|DTR|Money|Leader|X|Y|Z|Kills|Deaths):\s(\S+)$'
        regpl = r'^(Faction|Balance|Last Seen|Kills|Deaths):\s(.+)$'
        regpr = r'(?:player|faction)\.php\?(?:username|faction)=(.+)'

        self.factionRegex = re.compile(regfc, re.IGNORECASE)
        self.playerRegex  = re.compile(regpl, re.IGNORECASE)
        self.urlParser    = re.compile(regpr, re.IGNORECASE)

    def skipCache(self, url):
        """
        Determines whether or not to ignore the cache and re-download
        """

        try:
            if (arrow.now(self.highlifesTimezone) - self.cacheTimeouts[url]).total_seconds() > 60:
                self.cacheTimeouts[url] = arrow.now(self.highlifesTimezone)
                return True
        except KeyError:
            self.cacheTimeouts[url] = arrow.now(self.highlifesTimezone)
            return True

        return False

    def getPage(self, url, attempts=5):
        try:
            return requests.get(url, headers=self.headers)
        except HTTPError as e:
            if e.response.status_code in [502, 503, 504]:
                return getPage(url, attempts - 1)
            else:
                return None

    def autoSearch(self, obj, regex, string):
        """
        Adds fields to obj.data (dict) from regex pattern
        """
        matches = re.search(regex, string)

        # Try to convert data in list to a int, if that fails, try it as a float,
        # if that also fails, store it as a string
        try:
            obj.data[matches.group(1)] = int(matches.group(2))
        except ValueError:
            try:
                obj.data[matches.group(1)] = float(matches.group(2))
            except ValueError:
                try:
                    obj.data[matches.group(1)] = arrow.get(matches.group(2), 'MM/DD/YYYY HH:mm:ss')
                except arrow.parser.ParserError:
                    obj.data[matches.group(1)] = matches.group(2)
        except IndexError:
            pass
        except AttributeError:
            pass

    def getFaction(self, name, getPlayers=False):
        url = 'http://hcfactions.net/faction?faction=' + name

        if self.skipCache(url):
            page = self.getPage(url)
            s = BeautifulSoup(page.content)

            content = s.find(id='content')

            faction = Faction(name)

            # Get attributes
            for item in content.find_all('li'):
                self.autoSearch(faction, self.factionRegex, item.getText())

            # Add players to faction object
            if getPlayers:
                for header in content.find_all('h1'):
                    if header.getText() == 'Members':
                        for link in header.findNext('table').find_all('a'):
                            match = re.search(self.urlParser, link.get('href'))

                            try:
                                username = match.group(1)
                                faction.players.append(self.getPlayer(username))
                            except IndexError:
                                pass
                            except AttributeError:
                                pass

            self.factionCache[name] = faction

            return faction

        else:
            return self.factionCache[name]

    def getPlayer(self, username):
        url = 'http://hcfactions.net/player.php?username=' + username

        if self.skipCache(url):
            page = self.getPage(url)
            s = BeautifulSoup(page.content)

            content = s.find(id='content')

            player = Player(username)

            for item in content.find_all('li'):
                self.autoSearch(player, self.playerRegex, item.getText())

            self.playerCache[username] = player

            return player

        else:
            return self.playerCache[username]