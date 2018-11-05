#!/usr/bin/env python3
"""
originally from: https://gist.github.com/bradmontgomery/2219997

Very simple HTTP server in python.
Usage::
    ./dummy-web-server.py [<port>]
Send a GET request::
    curl http://localhost
Send a HEAD request::
    curl -I http://localhost
Send a POST request::
    curl -d "foo=bar&bin=baz" http://localhost
"""
from http.server import ThreadingHTTPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import os.path
import json
import threading

import logging
FORMAT = r"[%(asctime)20s:%(funcName)20s] %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG, style='%')
logger = logging.getLogger(os.path.basename(os.path.realpath(__name__)))

from classProperty import class_property

class actionModes():
    requestConfig = 'getConfig'
    postConfig = 'setConfig'
    # setTime = 'setTime' # for use with changing the sytem time


class HandlerObserver(object):
    def __init__(self):
        object.__init__(self)

    def handled_Get(self, path):
        raise NotImplemented("handled_Get not implemented")

    def handled_Post(self, path):
        raise NotImplemented("handled_Get not implemented")


class Handler(BaseHTTPRequestHandler):

    @class_property
    def _observer(cls):
        return cls._observer

    @_observer.setter
    def _observer(cls, value):
        if not isinstance(value, HandlerObserver):
            raise Exception("_observer must be of type HandlerObserver")
        cls._observer = value
        return cls._observer


    def _set_headers(self, code=200, message=''):
        self.send_response(code, message)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self._write("<html><body><h1>hi!</h1></body></html>")
        logger.debug('Received: ' + self.path)
        query_components = parse_qs(urlparse(self.path).query)
        logger.debug(json.dumps(query_components))

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers(400, 'Post not supported')

    def _write(self, message):
        self.wfile.write(bytes(message, 'UTF-8'))


class AlarmServer(HandlerObserver):
    def __init__(self, server_class=ThreadingHTTPServer, handler_class=Handler, port=1024):
        server_address = ('', port)
        self.httpd = server_class(server_address, handler_class)
        self.worker = threading.Thread(target=self.run_server(), args=())

        logger.info('Starting httpd...')
        logger.info('127.0.0.1:' + str(port))
        handler_class._observer = self
        self.start_server()

    def _cleanup(self):
        if self.httpd is None:
            return
        self.httpd.shutdown()
        self.worker.join(1)
        if self.worker.is_alive():
            self.worker.abort()
        self.httpd = None

    def _run_server(self):
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            print('Received shutdown command..')
            self.httpd.shutdown()
            print('Server shutdown.')
            raise
        self._cleanup()

    def start_server(self):
        self.worker.daemon = True
        self.worker.start()

    def stop_server(self):

        self._cleanup()


def run(server_class=ThreadingHTTPServer, handler_class=Handler, port=1024):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    logger.info('Starting httpd...')
    logger.info('127.0.0.1:' + str(port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Received shutdown command..')
        httpd.shutdown()
        print('Server shutdown.')
        raise


if __name__ == "__main__":
    # TODO: use argparse for port and verbosity.
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
