#! /usr/bin/env python

from commands import getoutput
from thread import allocate_lock

# ------------------------------------------------------------------------------
# some konstants
# ------------------------------------------------------------------------------

CHANNELS = ['#esp', '#esp-core']

SVNCHAN = ['#esp']
SVNLOOK = 'svnlook'
VIEWSVN = 'http://r.plexnet.org/%s'

REPOSITORY = '/var/www/svn.plexnet.org/htdocs/repos/'

NICK = NAME = 'xena'
LAST = None
LOCK = allocate_lock()

SERVER_HOST = 'irc.freenode.net'
SERVER_PORT = 8000

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
# utility funktion for querying an svn repository
# ------------------------------------------------------------------------------

def get_text_to_send():
    """Return text about the latest svn revision."""

    if LOCK.locked():
        return

    LOCK.acquire()

    try:

        global LAST

        if LAST is None:
            LAST = int(getoutput('%s youngest %s' % (SVNLOOK, REPOSITORY)).strip())
            return
                               
        revision = LAST + 1

        # the fundamentals
        info = getoutput(
            '%s info -r %s %s' % (SVNLOOK, revision, REPOSITORY)
            ).splitlines()

        if len(info) == 1:
            return

        LAST = revision
        author = info[0]
        log = info[3]

        # the revision changes
        changes = getoutput(
            '%s changed -r %s %s' % (SVNLOOK, revision, REPOSITORY)
            ).splitlines()

        number_of_changes = len(changes)

        # the changed directories
        dir_changes = getoutput(
            '%s dirs-changed -r %s %s' % (SVNLOOK, revision, REPOSITORY)
            ).splitlines()

        number_of_dirs = len(dir_changes)

        # we find the largest common parent directory
        subdir = None

        for path in dir_changes:
            if not subdir: subdir = path
            while not subdir in path:
                subdir = '/'.join(subdir.split('/')[:-1])

        if not subdir[-1:] == '/':
            subdir += '/'

        # some additional info
        files = []
        change_dict = {'changed': 0, 'added': 0, 'removed': 0}

        for ob in changes:

            if ob[-1] != '/': # i.e. if it's a file
                files.append((ob[4:].split('/')[-1], ob[:2].strip()))
                if ob[0] == 'A':
                    change_dict['added'] += 1
                elif ob[0] == 'D':
                    change_dict['removed'] += 1
                else:
                    change_dict['changed'] += 1

        # the message
        text = '%s by [%s]' % (VIEWSVN % revision, author)

        if number_of_dirs > 1:
            text += ' in %i subdirs of %s' % (number_of_dirs, subdir)
        else:
            text += ' in %s' % subdir

        # text += ' -- %r ' % log

        change_log = []
        for change_state in ['changed', 'added', 'removed']:
            if change_dict[change_state]:
                change_log.append(
                    '%i %s' % (change_dict[change_state], change_state)
                    )

        if change_log:
            text += ' -- [%s] ' % ', '.join(change_log)
            changed = ''
        else:
            changed = ' -- '

        if files:

            msglen = len(text)
            extra = []
            ellipsed = False

            for file in files:
                if (msglen + len(file[1]) + 9) > 480:
                    ellipsed = True
                    break
                msglen += len(file[1]) + 9
                extra.append('%s (%s)' % file)

            text += changed + ', '.join(extra)
            if ellipsed:
                text += ' ...'

        return text

    finally:
        LOCK.release()

# ------------------------------------------------------------------------------
# xena!
# ------------------------------------------------------------------------------

class Xena(Bot):

    def dispatch(self, origin, args):
        bytes, event, args = args[0], args[1], args[2:]
        if event == '251':
            print 'Joining channels:', CHANNELS
            for channel in CHANNELS:
                self.write(('JOIN', channel))
        elif event == 'PRIVMSG':
            text = get_text_to_send()
            if text:
                for channel in SVNCHAN:
                    self.msg(channel, text)

# ------------------------------------------------------------------------------
# self runner
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    #LAST = 12
    #for i in range(30):
    #    LAST = i
    #    print get_text_to_send()
    xena = Xena(NICK, NAME, CHANNELS)
    xena.run(SERVER_HOST, SERVER_PORT)
