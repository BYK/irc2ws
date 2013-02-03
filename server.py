# coding: utf-8

import logging
import socket

from tornado.ioloop import IOLoop
from tornado.iostream import IOStream
from tornado.web import Application
from tornado.websocket import WebSocketHandler


class WS2IRCBridge(WebSocketHandler):
    def open(self, host='irc.freenode.net', port=6667):
        self.sock = IOStream(socket.socket(socket.AF_INET,
                                           socket.SOCK_STREAM, 0))
        self.sock.connect((host, port), self.sock_loop)
        logging.debug("Request received for %s:%d", host, port)

    def sock_loop(self, data=None):
        if data:
            self.write_message(data)
        if self.sock.closed():
            self.close()
        else:
            self.sock.read_until("\r\n", self.sock_loop)

    def on_message(self, message):
        self.sock.write(message.encode('utf-8') + "\r\n")

    def on_close(self):
        self.sock.close()


if __name__ == "__main__":
    settings = {
        'auto_reload': True,
    }

    application = Application([(r'/([^:]*)', WS2IRCBridge)], **settings)
    application.listen(9090)
    IOLoop.instance().start()
