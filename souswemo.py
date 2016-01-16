#!/usr/bin/env python
import sys
import datetime
import time
import ouimeaux
import random
from threading import Thread
from w1thermsensor import W1ThermSensor
from ouimeaux.environment import Environment

accuracy = 15 # Check temp every 15seconds

def help():
    print("Usage: ./souswemo.py <WeMo_switch_name> <target>[C/F] <timer_minutes> ")
    print("Example: ./souswemo.py 'Slow Cooker' 60C 120")
    print("\nList available switches: ./souswemo.py -l")

def listSwitches(env):
    print("Available switch names are:")
    print(env.list_switches())

def getTemp():
    sensor = W1ThermSensor()            # Picks the first available sensor
    degrees = sensor.get_temperature()
    return degrees

def switchOn(switch):
    if getSwitch(switch) is False:
        print("Turning %s on" % switch.name)
        result = switch.basicevent.SetBinaryState(BinaryState=1)
        if result['BinaryState'] == "Error":
            print("Error: Couldn't turn %s on" % switch.name)
    else:
        print("Switch is already on")

def switchOff(switch):
    if getSwitch(switch) is True:
        print("Turning %s off" % switch.name)
        result = switch.basicevent.SetBinaryState(BinaryState=0)
        if result['BinaryState'] == "Error":
            print("Error: Couldn't turn %s off" % switch.name)
    else:
        print("Switch is already off")

def getSwitch(switch):
    result = switch.get_state(force_update=True)
    if result == 1:
        return True
    elif result == 0:
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
            print("Current temp: %sC @ %s - Switch %s is %s" % (currentTemp, time.strftime("%I:%M %p", time.localtime()), switch.name, currentState))
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
    print("Finding WeMo switches")
    global env
    env = Environment()
    env.start()
    env.discover(seconds=4)

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
        targetScale = sys.argv[2][-1]
        if targetScale == "F":
            targetF = int(sys.argv[2][:-1])
            # Convert to celsius because we're not American
            target = ((targetF - 32) / 1.8)
        elif targetScale == "C":
            target = int(sys.argv[2][:-1])
        else:
            print("Error: Please specify either [C]elsius or [F]ahrenheit")
            exit(1)
        timer = (int(sys.argv[3]) * 60)
    except:
        help()
        exit(1)

    while getTemp() < target:
        if getSwitch(switch) == False:
            switchOn(switch)
        print("Heating up. Current temp: %sC" % getTemp())
        time.sleep(accuracy)

    print("Device on switch %s is at target temperature %s" % (switchName, getTemp()))
    switchOff(switch)

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
        time.sleep(accuracy)
        currentTime = time.time()
        temp.append(getTemp())
        timeLeft = (startTime + timer) - currentTime
        if (round(timeLeft)/60) < 15:
            print("%s minutes left" % (round(timeLeft/60,0)))
    m.terminate()       # Kill the maintainTemp loop once timer finished
    t1.join()           # Join the maintainTemp thread with main
    switchOff(switch)   # We've finished. Turn the switch off, no matter the current state.
    average = sum(temp)/len(temp)
    print("Timer %s mins reached. Switch %s is now off" % ((timer/60), switch.name))
    print("Average temperature was %sC with a %s second accuracy" % (round(average,3),accuracy))


if __name__ == "__main__":
    main()
