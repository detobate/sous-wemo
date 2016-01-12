#!/usr/bin/env python
import sys
import datetime
import time
import ouimeaux
from threading import Thread
from w1thermsensor import W1ThermSensor
from ouimeaux.environment import Environment
from ouimeaux.utils import matcher
from ouimeaux.signals import receiver, statechange, devicefound


accuracy = 10 # Check temp every 30seconds
finished = False

def help():
    print("Usage: ./souswemo.py <WeMo_switch_name> <target>[C/F] <timer_minutes> ")
    print("Example: ./souswemo.py 'Slow Cooker' 60C 120")

def getTemp():
    # Pick the first available sensor
    #sensor = W1ThermSensor()
    #degrees = sensor.get_temperature()
    degrees = 60
    return degrees

def switchOn(switchName):
    print("Turning %s on" % switchName)
    return True

def switchOff(switchName):
    print("Turning %s off" % switchName)
    return True

def getSwitch(switchName):
    return False

class maintainTemp:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self, switchName, target):
        while self._running:
            currentTemp = getTemp()
            print("Current temp: %s" % currentTemp)
            if currentTemp < target and getSwitch(switchName) is False:
                switchOn(switchName)
            elif currentTemp < target and getSwitch(switchName) is True:
                pass
            elif currentTemp >= target and getSwitch(switchName) is True:
                switchOff(switchName)
            elif currentTemp >= target and getSwitch(switchName) is False:
                pass
            time.sleep(accuracy)

def main():
    if len(sys.argv) != 4:
        help()
        exit(1)

    switchName = sys.argv[1]
    origTarget = sys.argv[2]
    try:
        if sys.argv[2][-1] == "F":
            targetF = int(sys.argv[2][:-1])
            # Convert to celsius because we're not American
            target = ((targetF - 32) / 1.8)
        elif sys.argv[2][-1] == "C":
            target = int(sys.argv[2][:-1])
        else:
            print("Error: Please specify either [C]elsius or [F]ahrenheit")
            exit(1)
        timer = (int(sys.argv[3]) * 60)
    except:
        help()
        exit(1)

    while getTemp() < target:
        if getSwitch == False:
            switchOn(switchName)
        time.sleep(accuracy)

    print("Device on switch %s is at target temperature %s" % (switchName, origTarget))

    # Start the temp maintainer thread
    # Catch exit exceptions when timer expires
    m = maintainTemp()
    t1 = Thread(target=m.run, args=(switchName, target))
    t1.setDaemon(True)
    t1.start()

    raw_input("Press Enter to start the %s minute timer\n" % timer)
    startTime = int(time.time())
    currentTime = startTime
    temp = [] # Build a list to keep track of temperature
    print("Timer started, start time: %s\n" % startTime)
    while currentTime < (startTime + timer):
        temp.append(getTemp())
        currentTime = time.time()
        time.sleep(accuracy)

    m.terminate()   # Kill the maintainTemp loop
    t1.join()       # Join the maintainTemp thread with main
    # We've finished. Turn the switch off
    switchOff(switchName)
    average = sum(temp)/len(temp)
    print("Timer %s mins reached. Switch %s is now off" % ((timer/60), switchName))
    print("Average temperature was %s with a %s second accuracy" % (average,accuracy))


if __name__ == "__main__":
    main()
