#!/usr/bin/python
# -*- coding: utf-8 -*-
# __author__ = 'DusX'

import logging
import time
import socketIO_client
# import json

# https://docs.python.org/2/library/logging.html # LIST OF LEVELS
# logging.basicConfig(level='DEBUG')
# logging.basicConfig(level='INFO')
# logging.basicConfig(level='ERROR')


class WikiStream(socketIO_client.BaseNamespace):
    # def __init__(self):


    def on_reconnect(self, *args):
        self.emit('subscribe', '*')

    def on_connect(self):
        self.startT = time.clock()
        self.perMinute = 0
        self.minuteList = []
        self.runLen = 1  # only passed param: number of minutes to check
        self.outputstate = 3  # used for print statements (to minimize the draw time), 3 is final stage of phases and thus the start
        self.emit('subscribe', '*')
        print("minutes= " + str(self.runLen))

    def on_change(self, change):
        global socketIO # defined in the run code section.
        self.currentT = time.clock()

        if (self.currentT - self.startT) >= 60:
            print('data' + str(len(self.minuteList)) + ': ' + str(self.currentT - self.startT) + " - " + str(self.perMinute))  # print something per minute
            self.startT = time.clock()  # reset timer
            self.minuteList.append(self.perMinute)  # add minute count to list
            self.perMinute = 0 # reset count
            if len(self.minuteList) == self.runLen:
                # STOP PROCESS, Output totals.
                print("num of min past: " + str(len(self.minuteList)) + "   Max mins to read: " + str(self.runLen) )
                print(self.minuteList)
                socketIO.disconnect()
                exit()
                # return self.minuteList
        elif (self.currentT - self.startT) >= 45 and (self.currentT - self.startT) < 60 and  self.outputstate == 2:
            self.outputstate = 3
            print('3/4 : ' + str((self.currentT - self.startT)) + '--' + str(self.outputstate))

        elif (self.currentT - self.startT) >= 30 and (self.currentT - self.startT) < 45 and  self.outputstate == 1:
            self.outputstate = 2
            print('1/2 : ' + str((self.currentT - self.startT)) + '--' + str(self.outputstate))

        elif (self.currentT - self.startT) >= 15 and (self.currentT - self.startT) < 30 and  self.outputstate == 0:
            self.outputstate = 1
            print('1/4 : ' + str((self.currentT - self.startT)) + '--' + str(self.outputstate))

        elif (self.currentT - self.startT) >= 0 and (self.currentT - self.startT) < 15 and self.outputstate == 3:
            self.outputstate  = 0
            print('new : ' + str((self.currentT - self.startT)) + '--' + str(self.outputstate))

        self.perMinute +=1  # add to count (because new message arrived)


# https://www.mediawiki.org/wiki/API:Recent_changes_stream
# https://wikitech.wikimedia.org/wiki/Stream.wikimedia.org  # alt content options
# http://app.datasift.com/source/44/wikipedia # wikipedia content
#  https://dev.datasift.com/docs

if __name__ == "__main__":
    logging.basicConfig(level='ERROR')
    print("started as main")

    socketIO = socketIO_client.SocketIO('stream.wikimedia.org', 80)
    socketIO.define(WikiStream, '/rc')
    socketIO.wait()
    socketIO.disconnect(WikiStream, '/rc')
    # Disconnected
    # print("DONE")
else:
    print("started as other")
    print("this feature is not yet implemented")

