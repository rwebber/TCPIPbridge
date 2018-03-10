import win32gui, win32process, win32con

import psutil, sys



class dx_windows_tools(object):
    """
    This class defines methods for looking up windows handles/PIDs
    as well as, methods for sizing/moving windows
    """

    def __init__(self):
        pass

    # def get_winhandle_for_pid(self, pid):
    #     def callback(hwnd, cb_winhandle):
    #         if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
    #             _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
    #             if found_pid == pid:
    #                 cb_winhandle.append(hwnd)
    #         return True
    #     winhandle = []
    #     try:
    #         win32gui.EnumWindows(callback, winhandle)
    #     except:
    #         return None
    #     else:
    #         return winhandle

    def closeRecursive(self, PID):
        """
        close PID/window and all sub windows.
        :return:
        """
        try:
            for hwnd in self.get_hwnds_for_pid(PID):
                print hwnd, "=>", win32gui.GetWindowText(hwnd)
                win32gui.SendMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return 0
        except:
            return "error with closeRecursive"

    def get_hwnds_for_pid (self, pid):
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                #  found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    hwnds.append(hwnd)
            return True
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        # TODO: if more than 1 PID found, do a name lookup or something.??
        return hwnds

    def moveWindow(self, EXEprocess, width, height, x_pos, y_pos):

        hndl = 0   #setup value


        try:
            # hndl = self.get_winhandle_for_pid (EXEprocess.pid)[0]  # set to first entry in handle list.
            # hndl = self.get_hwnds_for_pid(EXEprocess.pid)[0]  # [0] auto extracts first option as output
            try:
                hndl = self.get_hwnds_for_pid(EXEprocess.pid)[0]  # treat as a list is returned
            except:
                pass # defer all errors !! bad idea
                    #TODO: fix this except statement
            else:
               #  hndl = self.get_hwnds_for_pid(EXEprocess.pid)  # NOT WORKING, returns [number]!!
                pass

        except:
            # failed to get PID
            hndl = "ERROR"
            return hndl
        else:

            if hndl == [] or hndl == 0:  # both lookups fails, so try the direct PID
                # empty set
                hndl = int(EXEprocess.pid)  # just incase its not an int yet

                state = psutil.pid_exists(hndl)
                if state:
                    p = psutil.Process(hndl)
                    count = p.num_handles()



            # if hndl is > 32 it was successful
            if hndl is None:
                return None  # operation failed
            elif hndl > 32:    # if greater that 32.. is good
                width = int(width)
                height = int(height)
                left = int(x_pos)
                top = int(y_pos)

                bottom = top + height
                right = left + width

                # find the screen resolution
                # http://timgolden.me.uk/python/win32_how_do_i/find-the-screen-resolution.html

                # SM_CXVIRTUALSCREEN
                # 78
                # The width of the virtual screen, in pixels.
                # The virtual screen is the bounding rectangle of all display monitors.
                # The SM_XVIRTUALSCREEN metric is the coordinates for the left side of the virtual screen.
                # https://msdn.microsoft.com/en-us/library/windows/desktop/ms724385(v=vs.85).aspx

                # also, this once get the edge of the virtual screen.. can be negative and likely helps with placement.
                # SM_XVIRTUALSCREEN  76

                # SM_CMONITORS
                # 80
                # The number of display monitors on a desktop. F
                # or more information, see the Remarks section in this topic.

                #left, top, right, bottom
                placement = (0, 1, (-32000, -32000), (-1, -1), (left, top, right, bottom))

                self.set_placement(hndl, placement)
                win32gui.ShowWindow(hndl, 1)

                placement = self.get_placement(hndl)  # sample value: tuple (0, 1, (-32000, -32000), (-1, -1), (0, 0, 656, 398))
                # print "Window placement: ", placement

                # http://msdn.microsoft.com/en-us/library/windows/desktop/ms632611%28v=vs.85%29.aspx

                # typedef struct tagWINDOWPLACEMENT {
                #  UINT  length;
                #  UINT  flags;
                #  UINT  showCmd;
                #  POINT ptMinPosition;
                #  POINT ptMaxPosition;
                #  RECT  rcNormalPosition;
                # } WINDOWPLACEMENT, *PWINDOWPLACEMENT, *LPWINDOWPLACEMENT;

                rect = win32gui.GetWindowRect(hndl)

                #x = rect[0]
                #y = rect[1]
                #w = rect[2] - x
                #h = rect[3] - y

                # return hndl
                return EXEprocess.pid  # hndl and pid are different and PID is needed for closing
            else:
                return None

    def get_placement(self, hndl):
        """
        Retrieve the window placement in the desktop.
        @see: L{set_placement}
        @rtype:  L{win32.WindowPlacement}
        @return: Window placement in the desktop.
        """
        return win32gui.GetWindowPlacement(hndl)

    def set_placement(self, hndl, placement):
        """
        Set the window placement in the desktop.
        @type  placement: L{win32.WindowPlacement}
        @param placement: Window placement in the desktop.
        @raise WindowsError: An error occurred while processing this request.
        """
        try:
            win32gui.SetWindowPlacement(hndl, placement)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        else:
            pass