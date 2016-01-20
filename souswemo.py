#!/usr/bin/env python
import sys
import datetime
import time
import ouimeaux
import random
import pygal
from threading import Thread
from w1thermsensor import W1ThermSensor
from ouimeaux.environment import Environment

accuracy = 15 # Check temp every 15seconds

def help():
    print("Usage: ./souswemo.py <WeMo_switch_name> <target>[C/F] <timer_minutes> [-f fudge%]")
    print("Example: ./souswemo.py 'Slow Cooker' 60C 120")
    print("\nOther options:")
    print(" -l \tList available WeMo switches")
    print(" -m \tMonitor current temperature")
    print(" -f \tFudge factor. Pre-emptively turn switch off/on. Provide value incl. suffix (C/F/%)")

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

def drawGraph(temp, outfile, targetScale):
    line_chart = pygal.Line()
    line_chart.title = "Temperature (in %s)" % targetScale

    timestamps = []
    tempvalues = []

    #Turn temp dictionary into individual ordered lists
    for key in sorted(temp):
        timestamps.append(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(key)))
        if targetScale == "F":
            value = value * 1.8 + 32
        tempvalues.append(temp[key])

    line_chart.x_labels = timestamps
    line_chart.add('Temperature', tempvalues)
    line_chart.render_to_png(outfile)


class watchTemp:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        while self._running:
            currentTemp = getTemp()
            print("Current temperature is %sC / %sF" % (currentTemp, (currentTemp * 1.8 + 32)))
            time.sleep(accuracy)

class maintainTemp:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self, switch, target, targetScale, lagValue):
        if lagValue is not None:
            if lagValue[-1] == "%":
                targetHigh = (target * (1 + (float(lagValue)/100)))
                targetLow = (target * (1 - (float(lagValue)/100)))
            elif lagValue[-1] == "F":
                targetHigh = (target + ((lagValue - 32) / 1.8))
                targetLow = (target - ((lagValue - 32) / 1.8))
            elif lagValue[-1] == "C":
                targetHigh = (target + lagValue)
                targetLow = (target - lagValue)
        else:
            targetHigh = target
            targetLow = target
        while self._running:
            currentTemp = getTemp()
            currentState = getSwitch(switch)
            if targetScale == "F":
                currentTemp = currentTemp * 1.8 + 32
            print("Current temp: %s%s @ %s - Switch %s is %s" % (currentTemp, targetScale, time.strftime("%I:%M %p", time.localtime()), switch.name, currentState))
            if currentTemp < targetHigh and currentState is False:
                switchOn(switch)
            elif currentTemp < targetHigh and currentState is True:
                pass
            elif currentTemp >= targetLow and currentState is True:
                switchOff(switch)
            elif currentTemp >= targetLow and currentState is False:
                pass
            time.sleep(accuracy)

def main():

    if sys.argv[1] == "-l":
        env = Environment()
        env.start()
        env.discover(seconds=4)
        listSwitches(env)
        exit(0)

    elif sys.argv[1] == "-m":
        print("Monitoring current temperatures every %s seconds" % accuracy)
        print("Press Enter to quit")
        m = watchTemp()
        t1 = Thread(target=m.run)
        t1.setDaemon(True)
        t1.start()
        raw_input()
        exit(0)

    elif len(sys.argv) < 4 or sys.argv[1] == "--help":
        help()
        exit(1)

    if "-f" in sys.argv and sys.argv[(sys.argv.index('-f')+1)]:
        if sys.argv[(sys.argv.index('-f')+1)]:
            lagValue = sys.argv[(sys.argv.index('-f')+1)][:-1]
        else:
            print("Please provide either a percentage of the target or an exact value for the fudge factor")
            print("eg. 1C, 10F, or 1%")
            exit(1)
    else:
        lagValue = None

    print("Finding WeMo switches")
    env = Environment()
    env.start()
    env.discover(seconds=4)

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
        if targetScale == "F":
            print("Heating up. Current temp: %sF" % (getTemp() * 1.8 + 32))
        else:
            print("Heating up. Current temp: %sC" % getTemp())
        time.sleep(accuracy)

    print("Device on switch %s is at target temperature %s" % (switchName, origTarget))
    switchOff(switch)

    # Start the temp maintainer thread
    # Catch exit exceptions when timer expires
    m = maintainTemp()
    t1 = Thread(target=m.run, args=(switch, target, targetScale, lagValue))
    t1.setDaemon(True)
    t1.start()

    raw_input("Press Enter to start the %s minute timer\n" % (timer/60))
    startTime = int(time.time())
    currentTime = startTime
    temp = {} # Build a dict to keep track of temperature
    print("Timer started, start time: %s\n" % time.strftime("%I:%M %p", time.localtime(startTime)))
    while currentTime < (startTime + timer):
        time.sleep(accuracy)
        currentTime = time.time()
        temp[time.time()] = getTemp()
        timeLeft = (startTime + timer) - currentTime
        if timeLeft > 0 and timeLeft < 60:
            print("%s seconds left" % int(round(timeLeft)))
        elif int(round(timeLeft)/60) == 1:
            print("1 minute left")
        elif (round(timeLeft)/60) < 15:
            print("%s minutes left" % int(round(timeLeft/60,1)))

    m.terminate()       # Kill the maintainTemp loop once timer finished
    t1.join()           # Join the maintainTemp thread with main
    switchOff(switch)   # We've finished. Turn the switch off, no matter the current state.
    average = sum(temp.values())/len(temp)
    if targetScale == "F":
        average = average * 1.8 + 32

    print("Timer %s mins reached. Switch %s is now off" % ((timer/60), switch.name))
    print("Average temperature was %s%s with a %s second accuracy" % (round(average,3), targetScale, accuracy))

    if "-o" in sys.argv:
        try:
            outfile = sys.argv[(sys.argv.index('-o') + 1)]
        except:
            print("No output filename provided")
            help()
            exit(1)
        drawGraph(temp, outfile, targetScale)

if __name__ == "__main__":
    main()
