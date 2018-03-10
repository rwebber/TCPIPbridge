#!/usr/bin/env python

# Runs a Tornado web server with a django project
# Make sure to edit the DJANGO_SETTINGS_MODULE to point to your settings.py

# http://stackoverflow.com/questions/2534603/how-use-django-with-tornado-web-server
# https://github.com/tamasgal/django-tornado

import sys
import os
import atexit

from tornado.options import options, define, parse_command_line
from tornado.escape import json_encode
import tornado.httpserver
import tornado.autoreload
import tornado.ioloop
import tornado.web
import tornado.wsgi
import random

from django.core.wsgi import get_wsgi_application


#TODO: use config ini for settings
define('port', type=int, default=8000)


class pingME(tornado.web.RequestHandler):  #  http://www.tornadoweb.org/en/stable/
    def __init__(self, application, request, **kwargs):
        super(pingME, self).__init__(application, request, **kwargs)
        self.message = ""

    def get(self):
        self.message = "ping: ", random.random()
        #self.write("hello, world")
        self.write(json_encode(self.message))


def main():

    try:  # ensure full process runs
        os.environ['DJANGO_SETTINGS_MODULE'] = 'TCPIP_bridge.settings' # TODO: edit this
        # sys.path.append('./bridgeApp') # path to your project if needed

        parse_command_line()

        BASE_DIR = os.path.dirname(os.path.dirname(__file__))

        """
        Details on the below usage of FallbackHandler for combining WSGI and Tornado
        http://www.tornadoweb.org/en/stable/web.html?highlight=django
        basically it allows DJANGO to run via WSGI(fallback), and other 'handlers' via Tornado (allowing async etc)
        Demo on github: https://github.com/bdarnell/django-tornado-demo/tree/master/testsite
         """
        wsgi_app = get_wsgi_application()
        container = tornado.wsgi.WSGIContainer(wsgi_app)
        settings = {'debug': True,
                    'static_path': os.path.join(BASE_DIR, 'static')}
        handlers = [
            ('/pingWebserver', pingME),  # http://IPaddress:8000/pingWebserver
            ('.*', tornado.web.FallbackHandler, dict(fallback=container))
        ]
        server = tornado.web.Application(handlers, **settings)
        server.listen(options.port)


        #TODO remove in prod
        tornado.autoreload.start()
        for d, _, files in os.walk('static'):  # d = directory
            [tornado.autoreload.watch(d + '/' + f) for f in files if not f.startswith('.')]


        print ("Launching IOLoop...")
        tornado.ioloop.IOLoop.current().start()

        on_shutdown() # only runs after a successful IOLoop.

    except:  # catch all... don't know what might go wrong?
        e = sys.exc_info()[0]
        print("Tornado Error: %s" % e)
    else:
        print("Unknown issue with Tornado Launch.")
    finally:
        print("Tornado main() complete")


def on_shutdown():
    print('Shutting down...')
    tornado.ioloop.IOLoop.instance().stop()


# maybe useful http://stackoverflow.com/questions/22314234/pyzmq-tornado-ioloop-how-to-handle-keyboardinterrupt-gracefully
# https://docs.python.org/2/library/atexit.html
@atexit.register
def cleanup():
    print('CleanUp:')
    on_shutdown()


if __name__ == '__main__':
    main()
