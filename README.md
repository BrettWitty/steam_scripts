These are scripts to examine your Steam collection.

linux.py
========

Counts how many of your games are Linux-friendly, and prints a small profile.

You'll need:
- [A Steam API Key](http://steamcommunity.com/dev/apikey)
- [requests](http://docs.python-requests.org/en/master/)
- [steamapi](https://github.com/smiley/steamapi/)
- [progressbar](https://pypi.python.org/pypi/progressbar/2.3)

`requests` and `progressbar` can be installed via `pip`. You need to follow the instructions on `steamapi` to get it installed.

This script produces `gamedata.json`, so you don't need to download it frequently.
