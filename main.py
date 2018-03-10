from kivy.garden.cefpython import CefBrowser, cefpython
# TODO: https://github.com/rentouch/cefkivy

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout

# Import the core and GUI elements of Qt
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *

# from django.core.management import call_command
# from django.core.wsgi import get_wsgi_application

import configCRUD  # config Definitions
import os, sys, subprocess, socket, psutil, random
from time import sleep, clock


# class BrowserLayout(BoxLayout):
#     def __init__(self, **kwargs):
#         super(BrowserLayout, self).__init__(**kwargs)

# ===================================================================================

if __name__ == '__main__':

    # should read its config data... http://kivy.org/docs/api-kivy.app.html
    # TODO: port the config over to Kivys version, and remove use of globals?? + a Settings Panel
    # will need to access host and port twice... ??
    path = "settings.ini"
    if not os.path.exists(path) :
        configCRUD.createConfig(path)
    host = configCRUD.readConfig(path, "tcpBridge", "host")
    port = configCRUD.readConfig(path, "tcpBridge", "port")

    # CHECK if PORT is already OPEN... likely because of Server already running.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex((host, int(port))) #returns 0 for open socket

    if result == 0:
        # TODO: test for keyword in Index page, to determine if runserver is already live.
        raise Exception('Required Socket is already open. See main.py s.connect_ex')
    else:
        # Closed socket, so time to open it.
        connected = False
        startT = clock()
        currentT = 0
        while not connected:
            try:
                if (currentT - startT) < 20:
                    # http://stackoverflow.com/questions/26207033/capture-stdout-of-django-runserver-with-popen
                    # djangoInst = subprocess.Popen(['python', './manage.py', 'runserver --noreload'], stdin=subprocess.PIPE, stdout=subprocess.PIPE) # runs as its own MAIN

                    currentT = clock() # since Popen is what may fail... adjust time first.

                    # djangoInst = subprocess.Popen(['python', './manage.py', 'runserver'], stdin=subprocess.PIPE, stdout=subprocess.PIPE) # runs as its own MAIN
                    djangoInst = subprocess.Popen(['python', './run_tornado.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE) # runs as its own MAIN

                    print("Wait for Server to Launch...")

                    while result != 0:  # WAIT until server is responsive, otherwise page may not load into CEF
                        print("Testing for webserver response...")
                        result = s.connect_ex((host, int(port)))

                    connected = True
                    PID = djangoInst.pid
                    print("PID value = " +str(PID))
                    print("Returncode = " +str(djangoInst.returncode))
                else:
                    raise Exception('TimeOut : launching webserver')

            except subprocess.CalledProcessError:
                print "Django Launch subprocessError"
                traceback.print_exc(file=sys.stdout)
                sys.exit(0)
            except OSError:
                print "Django Launch OSERROR"
                traceback.print_exc(file=sys.stdout)
                sys.exit(0)
            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise
    s.close()  #close the socket


    # setup Kivy app
    class CefBrowserApp(App):

        def __init__(self, **kwargs):
            super(CefBrowserApp, self).__init__(**kwargs)
            self.browser = False
            Clock.schedule_interval(self.poll, 90.)  # seconds

        def poll(self, *args):
            print("POLLLING FOR SERVER....")
            url = "http://127.0.0.1:8000/?v=" + str(int(random.random()*10000000))
            self.changeURL(url)  # requires HTTP
            pass

        def changeURL(self, url):
            # change_url(url)
            # https://code.google.com/p/cefpython/source/browse/cefpython/cef3/linux/binaries_64bit/kivy_.py
            self.browser.change_url(url)

        def build(self):
            global host, port
            startURL = "http://" + host + ":" + str(port)
            self.browser = CefBrowser(start_url=startURL)
            return self.browser


    class QTapp(object):
        def __init__(self):
            global host, port
            startURL = "http://" + host + ":" + str(port)
            app = QApplication([])
            win = QWebView()
            win.load(QUrl(startURL))
            win.show()
            app.exec_()


    CefBrowserApp().run()  # launch Kivy app - BLOCKING

    # app = QTapp()


    # test if  djangoInst is defined
    try:
        djangoInst
    except NameError:
        pass # djangoInst is undefined, somehow it wasn't launched above. ??
    else:
        # CLEAN UP django processes. http://eli.thegreenplace.net/2009/06/12/safely-using-destructors-in-python
        # https://docs.python.org/2/library/atexit.html  EXIT CODE
        # TODO: move all MAIN code to CLASS and create an instance of it in MAIN.. use destructor
        p = psutil.Process(PID)  # process handle of PID, manage.py Django handle
        pchildren = p.children(recursive=True)  #list of all children of ROOT PID
        for x in range(0, len(pchildren)):
            print("KILL child : " + "-" + str(pchildren[x].pid) +"....")
            t = psutil.Process(pchildren[x].pid)
            t.terminate()
        p.terminate()
        print("KILL : " + "-" + str(PID) +"....")
        djangoInst.kill()  # Close djangoInst process
        while djangoInst.poll() is None:  # None is returned while process is alive, wait for it to end.
            sleep(1.05)
        print djangoInst.returncode, "- djangoInst return code"

    cefpython.Shutdown()

    # import run_wsgiserver