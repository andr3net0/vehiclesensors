#!/usr/bin/python
# Copyright (c) 2017 Logicc Systems Ltd.
# Author: Andre Neto
  
import RPi.GPIO as GPIO  
from time import sleep
import subprocess
import time 
import getopt
import sys
import datetime
import pickle

try:
    import settings
except  Exception, e:
    print e
    print __name__ + ": Could not perform import"
    sys.exit(1)

try:
    CLEAR_WARN_PIN = settings.CLEAR_WARN_PIN
    verbose = settings.VERBOSE
    MAX_TIME = 30
    BUTTON_MIN_INTERVAL = 5 * 60
except:
    print "Could not read settings"
    sys.exit(1)

GPIO.setmode(GPIO.BCM)
warn = ''
player = None

# Define a threaded callback function
def my_callback(channel):
    if GPIO.input(channel):
        if verbose:
            print 'Button pressed'
        if player.poll() is None:
            player.stdin.write("q")
        try:
            last = datetime.datetime.now()
            f = open('buttonLastCall.pckl', 'wb')
            pickle.dump(last, f)
            f.close()
        except Exception as e:
            print e
        sys.exit()

def main(argv):
    global warn
    global player
    try:
        opts, args = getopt.getopt(argv,"hw:",["warn="])
    except getopt.GetoptError:
        print 'setSiren.py -w <warnType>'
        sys.exit(2)

    if len(opts) == 0:
        print 'setSiren.py -w <warnType>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'setSiren.py -w <warnType>'
            sys.exit()
        elif opt in ("-w", "--warn"):
            warn = arg

    if   warn == 'tempAbove':
        audioFile = "above.mp3"
    elif warn == 'tempBelow':
        audioFile = "below.mp3"
    elif warn == 'doorOpen':
        audioFile = "door.mp3"
    
    try:
        f = open('buttonLastCall.pckl', 'rb')
        last = pickle.load(f)
        f.close()
        diff = (datetime.datetime.now() - last).total_seconds()
        if verbose:
            print 'read last button call time'
            print last
            print 'minutes since last button call'
            print diff
    except:
        diff = 24*60*60
        if verbose:
            print 'no record from button call'

    if diff < BUTTON_MIN_INTERVAL:
        if verbose:
            print 'time since last button call not enough'
        sys.exit()

    try: 
        audioFile
    except NameError:
        print "no audio file defined"
        sys.exit()
    else:
        player = subprocess.Popen(["omxplayer", audioFile, "-o", "local", "--loop"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        GPIO.setup(CLEAR_WARN_PIN, GPIO.IN)
        GPIO.add_event_detect(CLEAR_WARN_PIN, GPIO.RISING, callback=my_callback, bouncetime=500)


    time.sleep(MAX_TIME)
    try:
        if player.poll() is None:
            player.stdin.write("q")
    except IOError as e:
        print e
    sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])