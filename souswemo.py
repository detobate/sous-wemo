#!/usr/bin/env python
import sys
import time
import ouimeaux
import argparse
import pygal
from threading import Thread
from w1thermsensor import W1ThermSensor
from ouimeaux.environment import Environment

parser = argparse.ArgumentParser(description='A WeMo control for sous-vide cooking')
parser.add_argument('--list', help='List available WeMo switches', action='store_true')
parser.add_argument('--mon', help='Monitor current temperature without controlling a switch', action='store_true')
parser.add_argument('-s', dest='switch', metavar="'Switch Name'", help='WeMo Switch Name')
parser.add_argument('-t', dest='temp', help='Target Temperature suffixed with either C or F')
parser.add_argument('-T', dest='time', type=int, help='Timer in minutes')
parser.add_argument('-f', dest='fudge', help='Fudge factor. Pre-emptively turn switch off/on. Provide value w/ suffix: C or F')
parser.add_argument('-a', dest='accuracy', type=int, default=15, help='How often to check the temperature in seconds (default 15)')
args = parser.parse_args()

if args.mon is True and args.list is True:
    parser.error("mon and list are mutually exclusive commands")


def listSwitches(env):
    print('Available switch names are:')
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

    accuracy = args.accuracy

    if args.list:
        env = Environment()
        env.start()
        env.discover(seconds=4)
        listSwitches(env)
        exit(0)

    elif args.mon:
        print("Monitoring current temperatures every %s seconds" % accuracy)
        print("Press Enter to quit")
        m = watchTemp()
        t1 = Thread(target=m.run)
        t1.setDaemon(True)
        t1.start()
        raw_input()
        exit(0)


    if args.fudge:
        lagValue = args.fudge[:-1]
    else:
        lagValue = None

    if args.switch and args.temp and args.time:

        print("Finding WeMo switches")
        env = Environment()
        env.start()
        env.discover(seconds=4)

        switchName = args.s
        origTarget = args.temp
        timer = (int(args.time) * 60)

        try:
            switch = env.get_switch(switchName)
        except:
            print("Couldn't find %s" % switchName)
            listSwitches(env)
            exit(1)

        try:
            targetScale = origTarget[-1]
            if targetScale == "F":
                targetF = int(origTarget[:-1])
                # Convert to celsius because we're not American
                target = ((targetF - 32) / 1.8)
            elif targetScale == "C":
                target = int(origTarget[:-1])
            else:
                print("Error: Please specify either [C]elsius or [F]ahrenheit")
                exit(1)
        except:
            parser.print_help()

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

        if args.o:
            try:
                outfile = args.o
            except:
                parse.help
            drawGraph(temp, outfile, targetScale)
    else:
        # If they haven't provided enough detail, print help
        print("\nYou must provide either --list, --mon, or all 3 of -s, -t and -T\n")
        parser.print_help()

if __name__ == "__main__":
    main()
