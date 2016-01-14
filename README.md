Sous-WeMo
========

A small script to control a [Belkin WeMo switch](http://www.belkin.com/uk/F7C027-Belkin/p/P-F7C027/) for [sous-vide cooking](https://en.wikipedia.org/wiki/Sous-vide).

Usage:
------
Install the required python modules:

    pip install -r requirements.txt

Usage:

    ./souswemo.py <WeMo_switch_name> <target>[C/F] <timer_minutes>

Example:

    ./souswemo.py 'Slow Cooker Switch' 60C 120

List Switches:

    ./souswemo.py -l
    Starting WeMo listen server
    Available switch names are:
    ['Big lights', 'Little lights', 'Slow Cooker Switch']

Requirements:
-------------
* [DS18B20](https://www.adafruit.com/search?q=DS18B20) One Wire temperature probe. (or other probes supported by the [w1thermsensor](https://github.com/timofurrer/w1thermsensor) Python module)
* A GPIO Interface, such as on a RaspberryPi or Beaglebone. [VirtGPIO](https://github.com/BLavery/virtual-GPIO) may work but hasn't been tested.
* Python2.7 and modules listed in [requirements.txt](https://raw.githubusercontent.com/detobate/sous-wemo/master/requirements.txt)


Example:
--------

    ./souswemo.py 'Big ball' 60C 1
    Starting WeMo listen server
    Turning Big ball on
    Heating up. Current temp: 60
    Device on switch Big ball is at target temperature 60C
    Turning Big ball off
    Press Enter to start the 1 minute timer
    Current temp: 60C @ 05:23 PM - Switch Big ball is False

    Timer started, start time: 05:23 PM

    Current temp: 61C @ 05:24 PM - Switch Big ball is False
    Current temp: 63C @ 05:24 PM - Switch Big ball is False
    Current temp: 60C @ 05:24 PM - Switch Big ball is False
    Current temp: 57C @ 05:24 PM - Switch Big ball is False
    Turning Big ball on
    Current temp: 61C @ 05:25 PM - Switch Big ball is True
    Turning Big ball off
    Switch is already off
    Timer 1 mins reached. Switch Big ball is now off
    Average temperature was 58 with a 15 second accuracy
