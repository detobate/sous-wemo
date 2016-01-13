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

accuracy = 10 # Check temp every 10seconds

def help():
    print("Usage: ./souswemo.py <WeMo_switch_name> <target>[C/F] <timer_minutes> ")
    print("Example: ./souswemo.py 'Slow Cooker' 60C 120")
    print("\nList available switches: ./souswemo.py -l")

def listSwitches(env):
    print("Available switch names are:")
    print(env.list_switches())

def getTemp():
    # Pick the first available sensor
    #sensor = W1ThermSensor()
    #degrees = sensor.get_temperature()
    degrees = 30
    return degrees

def switchOn(switch):
    print("Turning %s on" % switch.name)
    result = switch.basicevent.SetBinaryState(BinaryState=1)
    if result['BinaryState'] == 1:
        return True
    else:
        return False

def switchOff(switch):
    print("Turning %s off" % switch.name)
    result = switch.basicevent.SetBinaryState(BinaryState=0)
    if result['BinaryState'] == 0:
        return True
    else:
        return False
    return True

def getSwitch(switch):
    result = switch.get_state()
    if result == 1:
        return True
    else:
        return False

class maintainTemp:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self, switch, target):
        while self._running:
            currentTemp = getTemp()
            currentState = getSwitch(switch)
            print("Current temp: %sC @ %s" % (currentTemp, time.strftime("%I:%M %p", time.localtime())))
            if currentTemp < target and currentState is False:
                switchOn(switch)
            elif currentTemp < target and currentState is True:
                pass
            elif currentTemp >= target and currentState is True:
                switchOff(switch)
            elif currentTemp >= target and currentState is False:
                pass
            time.sleep(accuracy)

def main():
    print("Starting WeMo listen server")
    env = Environment()
    env.start()
    env.discover(seconds=1)

    if sys.argv[1] == "-l":
        listSwitches(env)
        exit(0)

    if len(sys.argv) != 4:
        help()
        exit(1)

    switchName = sys.argv[1]
    origTarget = sys.argv[2]

    try:
        switch = env.get_switch(switchName)
    except:
        print("Couldn't find %s" % switchName)
        listSwitches(env)
        exit(1)

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
        help(env)
        exit(1)

    while getTemp() < target:
        if getSwitch(switch) == False:
            switchOn(switch)
        time.sleep(accuracy)

    print("Device on switch %s is at target temperature %s" % (switchName, origTarget))

    # Start the temp maintainer thread
    # Catch exit exceptions when timer expires
    m = maintainTemp()
    t1 = Thread(target=m.run, args=(switch, target))
    t1.setDaemon(True)
    t1.start()

    raw_input("Press Enter to start the %s minute timer\n" % (timer/60))
    startTime = int(time.time())
    currentTime = startTime
    temp = [] # Build a list to keep track of temperature
    print("Timer started, start time: %s\n" % time.strftime("%I:%M %p", time.localtime(startTime)))
    while currentTime < (startTime + timer):
        temp.append(getTemp())
        currentTime = time.time()
        time.sleep(accuracy)

    m.terminate()   # Kill the maintainTemp loop
    t1.join()       # Join the maintainTemp thread with main
    # We've finished. Turn the switch off
    switchOff(switch)
    average = sum(temp)/len(temp)
    print("Timer %s mins reached. Switch %s is now off" % ((timer/60), switch.name))
    print("Average temperature was %s with a %s second accuracy" % (average,accuracy))


if __name__ == "__main__":
    main()
