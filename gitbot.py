#! /usr/bin/env python

"""GitHub/Dev IRC Bot."""

import simplejson
import traceback

from os.path import abspath, dirname, join as join_path
from posixpath import split as split_path
from Queue import Queue
from thread import allocate_lock, start_new_thread
from urllib import urlopen, quote as urlquote

from gitbotconfig import *

COMMITLOGS = {}

# ------------------------------------------------------------------------------
# httpserver.py from http://code.activestate.com/recipes/259148/
# ------------------------------------------------------------------------------

import asynchat, asyncore, socket, SimpleHTTPServer, select, urllib
import posixpath, sys, cgi, cStringIO, os, traceback, shutil

class CI_dict(dict):
    """Dictionary with case-insensitive keys
    Replacement for the deprecated mimetools.Message class
    """

    def __init__(self, infile, *args):
        self._ci_dict = {}
        lines = infile.readlines()
        for line in lines:
            k,v=line.split(":",1)
            self._ci_dict[k.lower()] = self[k] = v.strip()
        self.headers = self.keys()
    
    def getheader(self,key,default=""):
        return self._ci_dict.get(key.lower(),default)
    
    def get(self,key,default=""):
        return self._ci_dict.get(key.lower(),default)
    
    def __getitem__(self,key):
        return self._ci_dict[key.lower()]
    
    def __contains__(self,key):
        return key.lower() in self._ci_dict
        
class socketStream:

    def __init__(self,sock):
        """Initiate a socket (non-blocking) and a buffer"""
        self.sock = sock
        self.buffer = cStringIO.StringIO()
        self.closed = 1   # compatibility with SocketServer
    
    def write(self, data):
        """Buffer the input, then send as many bytes as possible"""
        self.buffer.write(data)
        if self.writable():
            buff = self.buffer.getvalue()
            # next try/except clause suggested by Robert Brown
            try:
                    sent = self.sock.send(buff)
            except:
                    # Catch socket exceptions and abort
                    # writing the buffer
                    sent = len(data)

            # reset the buffer to the data that has not yet be sent
            self.buffer=cStringIO.StringIO()
            self.buffer.write(buff[sent:])
            
    def finish(self):
        """When all data has been received, send what remains
        in the buffer"""
        data = self.buffer.getvalue()
        # send data
        while len(data):
            while not self.writable():
                pass
            sent = self.sock.send(data)
            data = data[sent:]

    def writable(self):
        """Used as a flag to know if something can be sent to the socket"""
        return select.select([],[self.sock],[])[1]

class RequestHandler(asynchat.async_chat, SimpleHTTPServer.SimpleHTTPRequestHandler):

    protocol_version = "HTTP/1.1"
    MessageClass = CI_dict

    def __init__(self,conn,addr,server):
        asynchat.async_chat.__init__(self,conn)
        self.client_address = addr
        self.connection = conn
        self.server = server
        # set the terminator : when it is received, this means that the
        # http request is complete ; control will be passed to
        # self.found_terminator
        self.set_terminator ('\r\n\r\n')
        self.rfile = cStringIO.StringIO()
        self.found_terminator = self.handle_request_line
        self.request_version = "HTTP/1.1"
        # buffer the response and headers to avoid several calls to select()
        self.wfile = cStringIO.StringIO()

    def collect_incoming_data(self,data):
        """Collect the data arriving on the connexion"""
        self.rfile.write(data)

    def prepare_POST(self):
        """Prepare to read the request body"""
        bytesToRead = int(self.headers.getheader('content-length'))
        # set terminator to length (will read bytesToRead bytes)
        self.set_terminator(bytesToRead)
        self.rfile = cStringIO.StringIO()
        # control will be passed to a new found_terminator
        self.found_terminator = self.handle_post_data
    
    def handle_post_data(self):
        """Called when a POST request body has been read"""
        self.rfile.seek(0)
        self.do_POST()
        self.finish()
            
    def do_GET(self):
        """Begins serving a GET request"""
        # nothing more to do before handle_data()
        self.body = {}
        self.handle_data()
        
    def do_POST(self):
        """Begins serving a POST request. The request data must be readable
        on a file-like object called self.rfile"""
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        self.body = cgi.FieldStorage(fp=self.rfile,
            headers=self.headers, environ = {'REQUEST_METHOD':'POST'},
            keep_blank_values = 1)
        self.handle_data()

    def handle_data(self):
        """Class to override"""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)

    def handle_request_line(self):
        """Called when the http request line and headers have been received"""
        # prepare attributes needed in parse_request()
        self.rfile.seek(0)
        self.raw_requestline = self.rfile.readline()
        self.parse_request()

        if self.command in ['GET','HEAD']:
            # if method is GET or HEAD, call do_GET or do_HEAD and finish
            method = "do_"+self.command
            if hasattr(self,method):
                getattr(self,method)()
                self.finish()
        elif self.command=="POST":
            # if method is POST, call prepare_POST, don't finish yet
            self.prepare_POST()
        else:
            self.send_error(501, "Unsupported method (%s)" %self.command)

    def end_headers(self):
        """Send the blank line ending the MIME headers, send the buffered
        response and headers on the connection, then set self.wfile to
        this connection
        This is faster than sending the response line and each header
        separately because of the calls to select() in socketStream"""
        if self.request_version != 'HTTP/0.9':
            self.wfile.write("\r\n")
        self.start_resp = cStringIO.StringIO(self.wfile.getvalue())
        self.wfile = socketStream(self.connection)
        self.copyfile(self.start_resp, self.wfile)

    def handle_error(self):
        traceback.print_exc(sys.stderr)
        self.close()

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects
        Set a big buffer size"""
        shutil.copyfileobj(source, outputfile, length = 128*1024)

    def finish(self):
        """Send data, then close"""
        try:
            self.wfile.finish()
        except AttributeError: 
            # if end_headers() wasn't called, wfile is a StringIO
            # this happens for error 404 in self.send_head() for instance
            self.wfile.seek(0)
            self.copyfile(self.wfile, socketStream(self.connection))
        self.close()

class Server(asyncore.dispatcher):
    """Copied from http_server in medusa"""
    def __init__ (self, ip, port,handler):
        self.ip = ip
        self.port = port
        self.handler = handler
        asyncore.dispatcher.__init__ (self)
        self.create_socket (socket.AF_INET, socket.SOCK_STREAM)

        self.set_reuse_addr()
        self.bind ((ip, port))

        # lower this to 5 if your OS complains
        self.listen (1024)

    def handle_accept (self):
        try:
            conn, addr = self.accept()
        except socket.error:
            self.log_info ('warning: server accept() threw an exception', 'warning')
            return
        except TypeError:
            self.log_info ('warning: server accept() threw EWOULDBLOCK', 'warning')
            return
        # creates an instance of the handler class to handle the request/response
        # on the incoming connexion
        self.handler(conn,addr,self)

# ------------------------------------------------------------------------------
# our request handler
# ------------------------------------------------------------------------------

class HookHandler(RequestHandler):

    def do_HEAD(self):
        self.send_error(501, "Unsupported method (HEAD)")

    def handle_data(self):

        try:
            content = self.handle_post_receive_hook()
        except Exception:
            import traceback
            traceback.print_exc()
            content = None

        if not content:
            self.send_error(404, "File Not Found")
            return

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def handle_post_receive_hook(self):

        path = self.path

        if path.startswith('/.github-post-receive-hook/'):
            key = path.split('/.github-post-receive-hook/', 1)[1]
            if key not in GITHUB_POST_RECEIVE_HOOK_KEYS:
                print "Unknown key:", key
                return
        else:
            return

        payload = self.body['payload'].value
        payload = simplejson.loads(payload)

        repository = payload['repository']['name']
        private = payload['repository']['private']

        if repository not in COMMITLOGS:
            COMMITLOGS[repository] = {
                'timestamp': '',
                'queue': Queue()
                }

        log = COMMITLOGS[repository]

        for commit in payload['commits']:

            item = {
                'repository': repository,
                'private': private,
                'id': commit['id'],
                'url': commit['url'],
                'author': commit['author']['name'],
                'message': commit['message'],
                'modified': commit['modified'],
                'added': commit['added'],
                'removed': commit['removed'],
                }

            if commit['timestamp'] > log['timestamp']:
                log['timestamp'] = commit['timestamp']

            log['queue'].put(item, False)
            
        return 'Thanks.'

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

def poll_dev_server(*args):
    try:
        _poll_dev_server(*args)
    except Exception:
        traceback.print_exc()


def _poll_dev_server(bot, origin, event, args, bytes):
    # print "#", time.time(), event, args, bytes
    # print " ", origin.nick, origin.user, origin.host, origin.sender
    check_commitlogs(bot)


def check_commitlogs(
    bot, with_url=WITH_URL, with_files=WITH_FILES,
    show_private_urls=SHOW_PRIVATE_URLS,
    update_file_path=join_path(dirname(abspath(__file__)), '.update')
    ):
    """Check the commit logs and message the IRC channels about it."""

    for repo, log in sorted(COMMITLOGS.items(), key=lambda x: x[1]['timestamp']):
        if repo not in GITHUB_REPOSITORIES:
            continue
        queue = log['queue']
        if not queue.empty():
            commit = queue.get()
            break
    else:
        return

    ref = None

    if ((not commit['private']) or show_private_urls) and with_url:
        try:
            ref = urlopen(TINYURL % urlquote(commit['url'])).read().strip()
        except Exception:
            pass

    if not ref:
        ref = commit['id'][:7]
        
    author = commit['author']
    author = NICKNAMES_MAPPING.get(author, author)

    added = [split_path(file) for file in commit['added']]
    modified = [split_path(file) for file in commit['modified']]
    removed = [split_path(file) for file in commit['removed']]

    message = commit['message']

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

    if subdir is None:
        subdir = '/'
    else:
        if not subdir.endswith('/'):
            subdir = subdir + '/'
        if not subdir.startswith('/'):
            subdir = '/' + subdir

    if with_files:

        files = []; append_file = files.append
        change_log = []

        for changeset, flag, flagtext in (
            (added, 'A', 'added'), (modified, 'U', 'modified'), (removed, 'D', 'removed')
            ):
            print flag, changeset, commit[flagtext]
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

    text = '%s by [%s]' % (ref, author)

    if number_of_dirs > 1:
        text += ' in %i subdirs of %s%s' % (
            number_of_dirs, repo, subdir
            )
    else:
        text += ' in %s%s' % (repo, subdir)

    text += ' -- %s' % message

    if change_log:
        text += ' -- [%s]' % ', '.join(change_log)

    if with_files and files:

        text += ' -- '
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

    for channel in GITHUB_REPOSITORIES[repo]:
        bot.msg(channel, text[:433])

    open(update_file_path, 'wb').close()

# ------------------------------------------------------------------------------
# dev bot!
# ------------------------------------------------------------------------------

class DevBot(Bot):

    _initialised = False
    _last_poll = 0
    _poll_lock = allocate_lock()
    _nick_rename_count = 0
    _currently_running = None

    def dispatch(self, origin, args):

        bytes, event, args = args[0], args[1], args[2:]

        if event == 'PRIVMSG':
            poll_dev_server(self, origin, event, args, bytes)
            self._last_poll = time.time()

        elif event == '251':
            print 'Joining channels:', self.channels
            self.msg('nickserv', 'identify %s' % NICKSERV_PASSWORD)
            for channel in self.channels:
                self.write(('JOIN', channel))
            self._initialised = True

        elif event == '433':
            self._nick_rename_count += 1
            self.write(('NICK', self.nick + ('`'*self._nick_rename_count)))

        else:
            if not self._initialised:
                return
            if (time.time() - self._last_poll) > MIN_POLL_DELAY:
                if self._poll_lock.locked():
                    return
                self._poll_lock.acquire()
                try:
                    poll_dev_server(self, origin, event, args, bytes)
                    self._last_poll = time.time()
                finally:
                    self._poll_lock.release()

    def handle_close(self):
        self.close()
        print >> sys.stderr, 'Closed!'
        time.sleep(3.0)
        DevBot.start()

    @classmethod
    def start(cls):

        if DevBot._currently_running is None:

            hook_server = Server(
                POST_RECEIVE_HOOK_SERVER_HOST,
                POST_RECEIVE_HOOK_SERVER_PORT,
                HookHandler
                )

            print "Post Receive Hook Server running on port %s" % POST_RECEIVE_HOOK_SERVER_PORT

            class FakeOrigin(object):
                def __init__(self):
                    self.nick = 'pokebot'
                    self.user = 'imaginary'
                    self.host = 'neverland'
                    self.sender = ':pokebot'

            origin = FakeOrigin()
            args = ('', 'POKE')

            def poke():
                while 1:
                    bot = DevBot._currently_running
                    if bot._initialised:
                        bot.dispatch(origin, args)
                    time.sleep(MIN_POLL_DELAY/3)

            start_new_thread(poke, ())

        bot = DevBot._currently_running = cls(NICK, NAME, CHANNELS)
        bot.run(SERVER_HOST, SERVER_PORT)

# ------------------------------------------------------------------------------
# self runner
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    DevBot.start()
