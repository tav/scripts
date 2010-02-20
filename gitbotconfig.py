NICK = NAME = 'plexdev'
CHANNELS = ['#esp', '#go-nuts']
NICKSERV_PASSWORD = 'm4r4k3shm5_k'

SERVER_HOST = 'irc.freenode.net'
SERVER_PORT = 8000

DEVLITE_SERVER = 'http://dev.plexnet.org'
DEVLITE_SERVER_KEY = 'e646fb8d4845467aa1219634cdf1ad1613181804f99b4391b5ba1a423'

MIN_POLL_DELAY = 1.0

GITHUB_REPOSITORIES  = {
    'blog': ['#esp'],
    'bootstrap': ['#esp'],
    'plexnet': ['#esp'],
    'scripts': ['#esp'],
    'webkit_titanium': ['#esp'],
    'webkit': ['#esp'],
    'espra': ['#esp'],
    'go': ['#go-nuts'],
    'ampify': ['#esp'],
    'ampdocs': ['#esp'],
    }

NICKNAMES_MAPPING = {
    'James Arthur': 'thruflo',
    'Mathew Ryden': 'oierw',
    'sbpalmer': 'sbp',
    'Sean B. Palmer': 'sbp',
    }

GITHUB_POST_RECEIVE_HOOK_KEYS = set([
    '69c2641b1b536f6b5f10211f74ea1dc52e9510b9824d13edfd7d1ab3d8b47fa3bf52427bd03b548a',
    '42bae7fe84ec8074aeabcf4a2bcc57d97bb652aa840e7094ac9a3950d55f8c941b2104ef6f2d1f36'
    ])

POST_RECEIVE_HOOK_SERVER_HOST = ''
POST_RECEIVE_HOOK_SERVER_PORT = 9090

TINYURL = 'http://is.gd/api.php?longurl=%s'

WITH_URL = True
WITH_FILES = True
SHOW_PRIVATE_URLS = True
