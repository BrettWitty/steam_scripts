import json
import os
import progressbar
import requests
import steamapi
import time

########################################
# Config variables you need to set
#

# You need to get your API key from http://steamcommunity.com/dev/apikey
# Terms of use: http://steamcommunity.com/dev/apiterms
if os.environ['STEAM_API_KEY']:
    API_KEY = os.environ['STEAM_API_KEY']
else:
    API_KEY = 'YOUR_API_KEY'

# We need either your Steam username or number
# Go to your Steam profile and copy the url. It'll either be:
#     http://steamcommunity.com/id/<username>/
# or
#     http://steamcommunity.com/profiles/<usernumber>
username = None
usernum = None

# When probing the application database, you are rate-limited to
# roughly one request per 1.5 sec. This multiplier is a 'niceness'
# scale. Above 1.0 is nicer but slower, below 1.0 is riskier.
NICENESS_SCALE = 1.1

########################################
########################################
# The script works in a few stages:
# 1. Connect to the Web API and get your basic information.
# 2. Print a little profile.
# 3. (Slowly) Query the Steam marketplace for Linux compatibility for
# each of your games/apps.


# Connect to the Web API
steamapi.core.APIConnection(api_key=API_KEY, validate_key=True)

# Retrieve my profile
if username:
    me = steamapi.user.SteamUser(userurl=username)
elif usernum:
    me = steamapi.user.SteamUser(usernum)
else:
    raise Exception("You need to set either username or usernum")

# Get your games list
games = me.games
numgames = len(me.games)

pb = progressbar.ProgressBar()

game_data = []
unsuccessful_appids = []

# Get the games info
for game in pb(games):

    appid = game.appid

    # We query the (unofficial) Steam store API
    # As described: https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI
    req_url = 'http://store.steampowered.com/api/appdetails/?appids={}'.format(appid)

    r = requests.get(req_url)

    try:

        # In case the request failed
        r.raise_for_status()

        data = r.json()[str(appid)]['data']

        game_data.append(data)

        # We pause for the API rate-limiting
        time.sleep( NICENESS_SCALE * (5*60.0) / 200 )

    except KeyError:
        unsuccessful_appids.append( appid )
        continue
    except requests.HTTPError:
        print("Request failed: {}".format(req_url))
        continue

# Save off data for later inspection
print("Saving data...")
with open('gamedata.json', 'wb') as f:
    json.dump(game_data, f)

# Compute data
linux_games = filter( lambda game: game['platforms']['linux'], game_data)
non_linux_games = filter( lambda game: not game['platforms']['linux'], game_data)
linux_count = len( linux_games )
missing_count = len(unsuccessful_appids)
total_count = len(game_data)

linux_pct = float(linux_count) / total_count

# Print some profile stats
profile_template = """
Profile:

Name: {profile.name}
ID: {profile.id}
Country: {profile.country_code}

Number of friends: {numfriends:,}
Number of groups: {numgroups:,}

Number of games owned: {numgames:,}
Number of Linux games owned: {linuxgames:,} ({pctlinux:0.2%})
Number of missing games: {missing}
"""

print( profile_template.format( profile=me,
                                numfriends=len(me.friends),
                                numgroups=len(me.groups),
                                numgames=total_count,
                                linuxgames=linux_count,
                                pctlinux=linux_pct,
                                missing=missing_count
))

linux_game_names = [ game['name'] for game in linux_games ]
linux_game_names.sort()

print(u"Linux games/apps I own:\n\t{}".format( u'\n\t'.join(linux_game_names) ))

non_linux_game_names = [ game['name'] for game in non_linux_games ]
non_linux_game_names.sort()

print(u"Non-Linux games/apps I own:\n\t{}".format( u'\n\t'.join(non_linux_game_names) ))

