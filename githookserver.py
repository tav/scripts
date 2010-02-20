from Queue import Queue

import simplejson

COMMITS = Queue()

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

        for commit in payload['commits']:
            item = {}
            item['repository'] = repository
            item['private'] = private
            item['url'] = commit['url']
            item['author'] = commit['author']['name']
            item['message'] = commit['message']
            item['modified'] = commit['modified']
            item['added'] = commit['added']
            item['removed'] = commit['removed']
            COMMITS.put(item, False)
            
        return 'Thanks.'


if __name__=="__main__":
    HTTP_SERVER_PORT = 9090
    s = Server('', HTTP_SERVER_PORT, HookHandler)
    print "SimpleAsyncHTTPServer running on port %s" % HTTP_SERVER_PORT
    try:
        asyncore.loop(timeout=2)
    except KeyboardInterrupt:
        print "Crtl+C pressed. Shutting down."
