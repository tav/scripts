#! /usr/bin/env python

"""An IRC notifier for GitHub repositories."""

from commands import getoutput
from posixpath import split as split_path
from thread import allocate_lock
from urllib import urlopen, quote as urlquote

import simplejson
import gitbotconfig

# ------------------------------------------------------------------------------
# some konstants
# ------------------------------------------------------------------------------

CHANNELS = ['#esp']

CHECK_INTERVAL = 60 # number of seconds between polling github
LAST_UPDATED = 0

NICK = NAME = 'gitpost'
LAST = None
LOCK = allocate_lock()

SERVER_HOST = 'irc.freenode.net'
SERVER_PORT = 8000

GITHUB_DATA = {}

WITH_URL = True # set this if you want urls in the irc message
WITH_FILES = False # set this if you want a file listing in the irc message

TINYURL = 'http://tinyurl.com/create.php?alias=github-%s&url=%s'
VIEWURL = 'http://tinyurl.com/github-%s'

# ------------------------------------------------------------------------------
# irc.py from http://inamidst.com/phenny/
# ------------------------------------------------------------------------------

import sys, re, time, traceback
import socket, asyncore, asynchat

class Origin(object): 
   source = re.compile(r'([^!]*)!?([^@]*)@?(.*)')

   def __init__(self, bot, source, args): 
      match = Origin.source.match(source or '')
      self.nick, self.user, self.host = match.groups()

      if len(args) > 1: 
         target = args[1]
      else: target = None

      mappings = {bot.nick: self.nick, None: None}
      self.sender = mappings.get(target, target)

class Bot(asynchat.async_chat): 
   def __init__(self, nick, name, channels): 
      asynchat.async_chat.__init__(self)
      self.set_terminator('\n')
      self.buffer = ''

      self.nick = nick
      self.user = nick
      self.name = name

      self.verbose = True
      self.channels = channels or []
      self.stack = []

      import threading
      self.sending = threading.RLock()

   def __write(self, args, text=None): 
      # print '%r %r %r' % (self, args, text)
      try: 
         if text is not None: 
            self.push(' '.join(args) + ' :' + text + '\r\n')
         else: self.push(' '.join(args) + '\r\n')
      except IndexError: 
         pass

   def write(self, args, text=None): 
      # This is a safe version of __write
      try: 
         args = [arg.encode('utf-8') for arg in args]
         if text is not None: 
            text = text.encode('utf-8')
         self.__write(args, text)
      except Exception, e: pass

   def run(self, host, port=6667): 
      self.initiate_connect(host, port)

   def initiate_connect(self, host, port): 
      if self.verbose: 
         message = 'Connecting to %s:%s...' % (host, port)
         print >> sys.stderr, message,
      self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
      self.connect((host, port))
      try: asyncore.loop()
      except KeyboardInterrupt: 
         sys.exit()

   def handle_connect(self): 
      if self.verbose: 
         print >> sys.stderr, 'connected!'
      self.write(('NICK', self.nick))
      self.write(('USER', self.user, '+iw', self.nick), self.name)

   def handle_close(self): 
      self.close()
      print >> sys.stderr, 'Closed!'

   def collect_incoming_data(self, data): 
      self.buffer += data

   def found_terminator(self): 
      line = self.buffer
      if line.endswith('\r'): 
         line = line[:-1]
      self.buffer = ''

      # print line
      if line.startswith(':'): 
         source, line = line[1:].split(' ', 1)
      else: source = None

      if ' :' in line: 
         argstr, text = line.split(' :', 1)
      else: argstr, text = line, ''
      args = argstr.split()

      origin = Origin(self, source, args)
      self.dispatch(origin, tuple([text] + args))

      if args[0] == 'PING': 
         self.write(('PONG', text))

   def dispatch(self, origin, args): 
      pass

   def msg(self, recipient, text): 
      self.sending.acquire()

      # Cf. http://swhack.com/logs/2006-03-01#T19-43-25
      if isinstance(text, unicode): 
         try: text = text.encode('utf-8')
         except UnicodeEncodeError, e: 
            text = e.__class__ + ': ' + str(e)
      if isinstance(recipient, unicode): 
         try: recipient = recipient.encode('utf-8')
         except UnicodeEncodeError, e: 
            return

      # No messages within the last 3 seconds? Go ahead!
      # Otherwise, wait so it's been at least 0.8 seconds + penalty
      if self.stack: 
         elapsed = time.time() - self.stack[-1][0]
         if elapsed < 3: 
            penalty = float(max(0, len(text) - 50)) / 70
            wait = 0.8 + penalty
            if elapsed < wait: 
               time.sleep(wait - elapsed)

      # Loop detection
      messages = [m[1] for m in self.stack[-8:]]
      if messages.count(text) >= 5: 
         text = '...'
         if messages.count('...') >= 3: 
            self.sending.release()
            return

      self.__write(('PRIVMSG', recipient), text)
      self.stack.append((time.time(), text))
      self.stack = self.stack[-10:]

      self.sending.release()

   def notice(self, dest, text): 
      self.write(('NOTICE', dest), text)

   def error(self, origin): 
      try: 
         import traceback
         trace = traceback.format_exc()
         print trace
         lines = list(reversed(trace.splitlines()))

         report = [lines[0].strip()]
         for line in lines: 
            line = line.strip()
            if line.startswith('File "/'): 
               report.append(line[0].lower() + line[1:])
               break
         else: report.append('source unknown')

         self.msg(origin.sender, report[0] + ' (' + report[1] + ')')
      except: self.msg(origin.sender, "Got an error.")

# ------------------------------------------------------------------------------
# utility funktion for querying github
# ------------------------------------------------------------------------------

def check_github_and_update(gitbot, with_url=WITH_URL, with_files=WITH_FILES):
    """Check GitHub for new commits and message the IRC channels about it."""

    event = None
    quiet = False

    reload(gitbotconfig)
    repositories = gitbotconfig.REPOSITORIES

    global LAST_UPDATED

    if LAST_UPDATED == 0:
       quiet = True

    for repo, channels in repositories.iteritems():

        if len(repo) == 2:
            repo = repo + ('master',)

        user, reponame, branch = repo

        if repo not in GITHUB_DATA:
            GITHUB_DATA[repo] = set()

        seen = GITHUB_DATA[repo]
        unseen = set()

        for commit in simplejson.loads(urlopen(
            'http://github.com/api/v1/json/%s/%s/commits/%s' % repo
            ).read())['commits']:
            commit_id = commit['id']
            if commit_id not in seen:
                unseen.add(commit_id)
                event = 1
            seen.add(commit_id)

        if quiet:
            continue

        for commit_id in unseen:

            shortcommit = commit_id[:8]

            commit_data = simplejson.loads(urlopen(
                'http://github.com/api/v1/json/%s/%s/commit/%s' % (user, reponame, commit_id)
                ).read())['commit']

            author = commit_data['committer']['name']
            added = [split_path(file['filename']) for file in commit_data['added']]
            modified = [split_path(file['filename']) for file in commit_data['modified']]
            removed = [split_path(file['filename']) for file in commit_data['removed']]
            message = commit_data['message']
            commiturl = commit_data['url']

            changes = added + modified + removed
            number_of_changes = len(changes)
            directories = set()

            for (directory, filename) in changes:
                directories.add(directory)

            number_of_dirs = len(directories)

            # we find the largest common parent directory
            subdir = None
            for path in directories:
                spath = '/' + path
                if not subdir: subdir = spath
                while not subdir in spath:
                    subdir = split_path(subdir)[0]
                    if not subdir.startswith('/'):
                        subdir = '/' + subdir

            if not subdir.endswith('/'):
                subdir = subdir + '/'

            if subdir == '/':
                subdir = ''

            if with_files:

                files = []; append_file = files.append
                change_log = []

                for changeset, flag, flagtext in (
                    (added, 'A', 'added'), (modified, 'U', 'changed'), (removed, 'D', 'removed')
                    ):
                    for file in changeset:
                        append_file('%s (%s)' % (file[1], flag))
                    if changeset:
                        change_log.append('%i %s' % (len(changeset), flagtext))

            else:

                change_log = []

                for changeset, flagtext in (
                    (added, 'added'), (modified, 'changed'), (removed, 'removed')
                    ):
                    if changeset:
                        change_log.append('%i %s' % (len(changeset), flagtext))

            # the message

            if with_url:
                text = '%s by [%s]' % (VIEWURL % shortcommit, author)
            else:
               text = author

            if number_of_dirs > 1:
                text = ' in %i subdirs of %s/%s/%s' % (
                    number_of_dirs, user, reponame, subdir
                    )
            else:
                text = ' in %s.%s/%s' % (user, reponame, subdir)

            if message.endswith('.'):
                message = message[:-1]
            text += ' -- %s' % message

            if change_log:
                text += ' -- [%s]' % ', '.join(change_log)

            if with_files and files:

                msg += ' -- '
                msglen = len(text)
                extra = []
                ellipsed = False

                for file in files:
                    if (msglen + len(file) + 6) > 433:
                        ellipsed = True
                        break
                    msglen += len(file) + 2
                    extra.append(file)

                text += ', '.join(extra)
                if ellipsed:
                    text += ' ...'

            if with_url:
               urlopen(TINYURL % (shortcommit, urlquote(commiturl))).read()

            for channel in channels:
                gitbot.msg(channel, text)

    LAST_UPDATED = time.time()

    if event:
       open('.update', 'wb').close()

# ------------------------------------------------------------------------------
# gitbot!
# ------------------------------------------------------------------------------

class GitBot(Bot):

    def dispatch(self, origin, args):
        bytes, event, args = args[0], args[1], args[2:]
        if event == '251':
            print 'Joining channels:', CHANNELS
            for channel in CHANNELS:
                self.write(('JOIN', channel))
        elif event == 'PRIVMSG':
           if (time.time() - LAST_UPDATED) > CHECK_INTERVAL:
              if LOCK.locked():
                 return
              LOCK.acquire()
              try:
                 check_github_and_update(self)
              finally:
                 LOCK.release()

# ------------------------------------------------------------------------------
# self runner
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    gitbot = GitBot(NICK, NAME, CHANNELS)
    gitbot.run(SERVER_HOST, SERVER_PORT)
