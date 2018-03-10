import random
import subprocess
import sys
import time

from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.generic import View
from django.views.generic import TemplateView  # subclass from if using defined template
from django.http import JsonResponse
from django.conf import settings

# system stuff
if sys.platform.startswith('win32'):
    import win32gui, win32con
if sys.platform.startswith('darwin'):
    pass  # import MAC system modules

# send as OSC
from simpleOSC import initOSCClient, initOSCServer, setOSCHandler, sendOSCMsg, closeOSC, \
    createOSCBundle, sendOSCBundle, startOSCServer

# screenCapture
from mss import mss

# custom Classes DusX
import dx_windows_tools as dxwt


# class Views
# ---------- https://docs.djangoproject.com/en/1.8/ref/class-based-views/base/
# !!! http://reinout.vanrees.org/weblog/2014/05/19/context.html

#  screenShot, displayShot
class DisplayCIF(View): # Display_Capture_Image_File

    def get(self, request, *args, **kwargs): # GET request
        print "API: DisplayCIF (Display_Capture_Image_File)"
        screencap = mss()

        path_to_file = request.GET.get('pfile', 'ScreenCapture_%d.png')  # defaultName saves to root of this application
        # the path can be absolute, allowing the file to be saved anywhere of the system
        # eg: pfile = "C:/Users/DusX/Desktop/testScreenCapture.png"
        # note: REQUIRES forward slashes!

        # TODO: test path_to_file for "\" and replace with "/"

        # TODO: wrap in try.. and set 'r' accordingly
        for filename in screencap.save(output='C:/Users/DusX/Desktop/testScreenCapture666.png', screen=2):
            # screen num matches as defined in Windows Display Settings
            print(filename)
            fname = filename

        # setup view types allowed: 'JSON', 'HTML'
        view = request.GET.get('view', "HTML")  # default to HTML for client

        r = 0  # use 0 to represent no error

        if view == "HTML":
            if r == 0:
                r = "Saved: " + fname
            template_name = 'api_DisplayCIF.html'
            return TemplateResponse(request, template_name, {"response": r})

        if view == "JSON":
            return JsonResponse({'response': r})


class ClosePID(View):

    def get(self, request, *args, **kwargs): # GET request
        print "API: ClosePID GET"
        # print request

        PID = request.GET.get('pid', None)  # expect INT or None

        if PID is None or PID == "None" or PID == "none" or PID == "NONE":  # cover options.. not GET val is as string
            r = "PID as None"
        else:
            PID = int(PID)  # ensure its seen as interger
            dx_wintools = dxwt.dx_windows_tools()

            if dx_wintools.closeRecursive(PID) == 0:
                r = 0  # use 0 to represent no error
            else:
                r = "Error closing windows"

        # setup view types allowed: 'JSON', 'HTML'
        view = request.GET.get('view', "HTML")  # default to HTML for client

        # CLOSE THE PID return value as response
        # response = None

        if view == "HTML":
            if r == 0:
                r = "window closed"
            template_name = 'api_closePID.html'
            return TemplateResponse(request, template_name, {"response": r})

        if view == "JSON":
            return JsonResponse({'response': r})


class Launch(TemplateView):
    # TODO: fix placement issue with handle from link below.
    # http://127.0.0.1:8000/api/Launch/?pexe=C%3A%5CProgram%20Files%20(x86)%5CSpout%5CMAXexe%5CspoutSend%5CspoutSend.exe

    def get(self, request, *args, **kwargs): # GET request
        print "API: Launch GET"
        print request

        # setup view types allowed: 'JSON', 'HTML'
        view = request.GET.get('view', 'HTML')  # default to HTML for client

        # path_to_EXE = r'C:\Windows\System32\notepad.exe'
        path_to_EXE = request.GET.get('pexe', 'notepad.exe')  # default to notepad since its usually on system path

        # path_to_file = 'README.txt'
        path_to_file = request.GET.get('pfile', '')  # default Blank

        # set window width and height
        win_width = request.GET.get('w', '640')  # default Blank
        win_height = request.GET.get('h', '480')  # default Blank

        # set window width and height
        x_pos = request.GET.get('x', '0')  # default Blank
        y_pos = request.GET.get('y', '0')  # default Blank

        # TODO: use DesktopMagic getDisplayRects() and test to ensure legal values  (if WINDOWS)

        print path_to_EXE
        print path_to_file

        # print passed args ---------------------------
        for count, thing in enumerate(args):
            print '{0}. {1}'.format(count, thing)
        for name, value in kwargs.items():
            print '{0} = {1}'.format(name, value)
        # ---------------------------------------------

        hndl = None

        try:
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = win32con.SW_SHOWMINIMIZED
            DETACHED_PROCESS = 0x00000008

            EXEprocess = subprocess.Popen(r"%s %s" % (path_to_EXE, path_to_file), startupinfo=info, creationflags=DETACHED_PROCESS, close_fds=True)
        except:
            # try:
            #     # a more simple launch
            #     EXEprocess = subprocess.Popen(r"%s %s" % (path_to_EXE, path_to_file))
            # except:
            #     # both fail so giveup
            #     hndl = "FAILURE:", r"%s %s" % (path_to_EXE, path_to_file)
            hndl = "FAILURE:", r"%s %s" % (path_to_EXE, path_to_file)
        else:
            # no error, so continue
            # TODO: Find better option than SLEEP
            time.sleep(1)  # sleep for X seconds
            dx_wintools = dxwt.dx_windows_tools()
            hndl = dx_wintools.moveWindow(EXEprocess, win_width, win_height, x_pos, y_pos) # Must launch to screen for most to open OpenGL context

        if view == "HTML":
            template_name = 'api_Launch.html'
            # return TemplateResponse(request, self.template_name, self.get_context_data(handle=hndl,))
            return TemplateResponse(request, template_name, self.get_context_data(handle=hndl,))

        if view == "JSON":
            return JsonResponse({'PID': hndl})

    def post(self, request, *args, **kwargs):
        # return HttpResponse("Launch Class POST")
        return "post"


    def get_context_data(self, *args, **kwargs):  # returns the context dictionary
        # Call the base implementation first to get a context
        context = super(Launch, self).get_context_data(**kwargs)
        # add to the data
        context['appName'] = "Launcher :)"
        print "^context^"
        # print passed args ---------------------------
        for count, thing in enumerate(args):
            print '{0}. {1}'.format(count, thing)
        for name, value in kwargs.items():
            print '{0} = {1}'.format(name, value)
        # ---------------------------------------------
        return context


# def views here.
def index(request):
    # return HttpResponse('<link rel="stylesheet" type="text/css" href="static/css/bootstrap.css">')
    return render(request, 'index.html', {})


def testJSON(request):
    # return HttpResponse('{"RPM": 555}')
    sample = random.randint(100, 999)
    return JsonResponse({'RPM': sample})


# sss_minute , samplesocketstream : returns JSON with number of samples received from stream in 1 MIN
# WARNING >>> BLOCKING process. It blocks everything for 1 min or TimeOut
def samplesocketstream(request):
    import subprocess
    import ast
    import time

    # use URL string VARS: http://stackoverflow.com/questions/150505/capturing-url-parameters-in-request-get
    # http://stackoverflow.com/questions/6164540/getting-two-strings-in-variable-from-url-in-django
    # https://docs.python.org/2/library/re.html
    # http://www.djangobook.com/en/2.0/chapter07.html

    if request.method == 'GET':

        #  C:\Users\DusX\CODE\python\TCPIP_bridge\bridgeApp\
        p = subprocess.Popen(["python", "-u", settings.DX_SOCKETSTREAMFILE],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1)

        startT = time.clock()
        print ("launched: " + p.stdout.readline()), # read the first line

        # prepar OSC server while Popen launching and processing
        initOSCClient('127.0.0.1',1234) # takes args : ip, port initOSCClient(ip='127.0.0.1', port=9000)

        hold = True  # setup for loop
        data = False  # setup for loop
        while hold: # repeat several times to show that it works
            currentT = time.clock()

            strOSC = "processing: " + str(currentT - startT)
            sendOSCMsg("/RPM", [strOSC])  # send text OSC

            if (currentT - startT) >= 70: #if it takes more than a minute+ we should timeout. time should relate to Izzy
                # TODO: should relaunch after killing process
                p.terminate()
                return HttpResponse("Socket TIMEOUT")  # untested for how Izzy handles this response

            data = p.stdout.readline() # read output
            print ("Line" + ": " + data)

            try:
                data = ast.literal_eval(data)
                print("data=: " + str(type(data)))
                if type(data) is list:
                    print("data match found.")
                    data = data[0]
                hold = False
            except:
                # add timeout code, incase
                data = False
                pass

        # print p.communicate("n\n")[0], # signal the child to exit,
        # print ("FINAL" + str(p.communicate()[0]))  # signal the child to exit, # read the rest of the output, # wait for the child to exit

        if data:
            if p:
                p.terminate()
                print("process terminated")
            # SEND OSC
            sendOSCMsg("/RPM", [data])  # !! it sends by default to localhost ip "127.0.0.1" and port 9000
            closeOSC()

            # return HttpResponse("RPM = " + str(data) + "\n")  # requests per minute
            return JsonResponse({'RPM': data})

    if request.method == 'POST':
        return HttpResponse("POST")
