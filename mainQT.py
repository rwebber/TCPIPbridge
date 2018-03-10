# setup LOCAL IP FOR MACHINE via router (see end of video)
# https://www.youtube.com/watch?v=gQdxxckMD4I


# Import the core and GUI elements of Qt
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *

# from django.core.management import call_command
# from django.core.wsgi import get_wsgi_application

import configCRUD  # config Definitions
import os, sys, subprocess, socket, psutil, atexit, random, traceback
from time import sleep, clock
import ctypes

# TODO: http://pythoncentral.io/intro-to-pysidepyqt-basic-widgets-and-hello-world/  #ADD JS integration and more.


class QTapp(object):

    def __init__(self):
        #super(QTapp, self).__init__()
        global host, port  # TODO: get rid of Globals, and pass args as needed.
            # self.setWindowIcon(QtGui.QIcon('MyGui.ico'))
        if os.name == 'nt':
            # define as python hosted app for Windows to allow Icon
            # see: http://stackoverflow.com/questions/17068003/application-icon-in-pyside-gui
            myappid = u'DusXproductions.tcpbridge.qtweb.v01'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        startURL = "http://" + host + ":" + str(port)
        app = QApplication([])
        window = QWebView()
        window.load(QUrl(startURL))
        window.resize(860, 600)
        window.setWindowTitle('TCPIP bridge')
        window.setWindowIcon(QIcon('TCPIP32.png'))
        window.show()
        app.exec_()


# https://docs.python.org/2/library/atexit.html
# http://sharats.me/the-ever-useful-and-neat-subprocess-module.html#auto-kill-on-death
#  TODO: !!! add cleanup to Web-server scripts.. eg: tornado needs to free socket on close.
@atexit.register
def cleanup():
    pass


if __name__ == '__main__':

    path = "settings.ini"
    if not os.path.exists(path) :
        configCRUD.createConfig(path)
    host = configCRUD.readConfig(path, "tcpBridge", "host")
    port = configCRUD.readConfig(path, "tcpBridge", "port")
    server = configCRUD.readConfig(path, "tcpBridge", "server") #tornado = T , django internal runserver = D

    # CHECK if PORT is already OPEN... likely because of Server already running.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex((host, int(port))) #returns 0 for open socket

    # global PID
    PID = None  # give default value so it is defined within all blocks, test for None as test

    if result == 0:
        # TODO: test for keyword in Index page, to determine if runserver is already live.
        s.shutdown(socket.SHUT_RDWR) # good chance this doesnt work.   Is 's'
        s.close()
        raise Exception('Required Socket is already open. See QTmain.py s.connect_ex')
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

                    currentT = clock()  # since Popen is what may fail... adjust time first.

                    # TODO: implement check_output for tornado.. During the while loop + TimeOut
                    # from subprocess import check_output
                    # out = check_output(["ntpq", "-p"])

                    if server == "T":
                        djangoInst = subprocess.Popen(['python', './run_tornado.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)  # runs as its own MAIN
                        print("Wait for Tornado webserver to Launch...")
                    if server == "D":
                        djangoInst = subprocess.Popen(['python', './manage.py', 'runserver'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)  # runs as its own MAIN
                        print("Wait for Django runserver to Launch...")

                    while result != 0:  # WAIT until server is responsive, otherwise page may not load into CEF
                        # TODO: add a timeout... !!
                        print("Testing for webserver response on port: " + str(port))
                        result = s.connect_ex((host, int(port)))

                    connected = True  # exit while

                    PID = djangoInst.pid

                    print("PID value = " +str(PID) + ", Returncode = " + str(djangoInst.returncode))
                    print(str(server) + ", Server running at: " + str(host) + " , port: " + str(port))

                    # for line in djangoInst.stdout:
                    #     print "testing:1:2:3:  "
                    #     print line

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


    app = QTapp() # Launch QT interface # BLOCKING !?
    

    # test if  djangoInst is defined
    try:
        djangoInst
    except Exception as error:
        # logger.error(error)
        print("django instance failure during launch. ")  # + error.args
        #  djangoInst is undefined, somehow it wasn't launched above. ??
        raise

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

    # import run_wsgiserver