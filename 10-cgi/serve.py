#!/usr/bin/env python3

import http.server
from http.server import HTTPServer, CGIHTTPRequestHandler
from socketserver import ThreadingMixIn

import urllib.request as reqs
import urllib.error
import sys
import os

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    #lel
    pass

class CGIHandler(CGIHTTPRequestHandler):
    cgi_directories = ['/']

    #.is_cgi - "is" method with side effects <3 
    #but I just follow the basic implementation in CGIHTTPRequestHandler
    def is_cgi(self):
        file = urllib.parse.urlparse(self.path).path
        if file[-4:].lower() == ".cgi":
            self.cgi_info = os.curdir, file
            return True
        return False

    def do_common(self):
        file = urllib.parse.urlparse(self.path).path[1:]
        if os.path.isfile(file):
            if self.is_cgi():
                self.run_cgi()
            else:
                f = open(file, 'br')
                self.send_response(200)
                self.send_header('Content-Length', str(os.stat(file).st_size))
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
        else:
            self.send_error(404)

    def do_GET(self):
        self.do_common()
    
    def do_POST(self):
        self.do_common()

    def do_HEAD(self):
        self.do_common()
    

port = 9001
# port = int(sys.argv[1])
dir = "" 
# dir = sys.argv[2]


dir = os.path.join(os.path.dirname(__file__), dir)
os.chdir(dir)

server = ThreadedHTTPServer(("", port), CGIHandler)
server.serve_forever()
