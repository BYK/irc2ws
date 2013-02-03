# coding: utf-8

import logging
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import socket

from tornado.iostream import IOStream


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        loader = tornado.template.Loader(".")
        self.write(loader.load("index.html").generate())


class WS2IRCBridge(tornado.websocket.WebSocketHandler):
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


application = tornado.web.Application([
    (r'/ws', WS2IRCBridge),
    (r"/", MainHandler),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": "./resources"}),
])

if __name__ == "__main__":
    application.listen(9090)
    tornado.ioloop.IOLoop.instance().start()
