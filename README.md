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
    ['Big lights', 'Little lights', 'Slow Cooker']

Requirements:
-------------
* Waterproof [DS18B20](https://www.adafruit.com/search?q=DS18B20) One Wire temperature probe. (or other probes supported by the [w1thermsensor](https://github.com/timofurrer/w1thermsensor) Python module)

Follow [these](http://www.modmypi.com/blog/ds18b20-one-wire-digital-temperature-sensor-and-the-raspberry-pi) instructions if using a RaspberryPi.
* A GPIO Interface, such as on a RaspberryPi or Beaglebone. [VirtGPIO](https://github.com/BLavery/virtual-GPIO) may also work but hasn't been tested.
* Python2.6 and modules listed in [requirements.txt](https://raw.githubusercontent.com/detobate/sous-wemo/master/requirements.txt)


Example:
--------

    ./souswemo.py 'Slow Cooker' 75C 360
    Finding WeMo switches
    Turning Slow Cooker Switch on
    Device on switch Slow Cooker Switch is at target temperature 75C
    Press Enter to start the 360 minute timer
    Current temp: 76.062C @ 01:51 PM - Switch Slow Cooker Switch is False

    Timer started, start time: 01:51 PM
    Current temp: 76.187C @ 01:51 PM - Switch Slow Cooker Switch is False
    Current temp: 76.062C @ 01:52 PM - Switch Slow Cooker Switch is False
    Current temp: 68.812C @ 01:52 PM - Switch Slow Cooker Switch is False
    Turning Slow Cooker Switch on
    ...
    Current temp: 74.875C @ 01:57 PM - Switch Slow Cooker Switch is True
    Current temp: 74.937C @ 01:57 PM - Switch Slow Cooker Switch is True
    Current temp: 75.0C @ 01:58 PM - Switch Slow Cooker Switch is True
    Turning Slow Cooker Switch off
    Current temp: 75.0C @ 01:58 PM - Switch Slow Cooker Switch is False
    Current temp: 75.0C @ 01:59 PM - Switch Slow Cooker Switch is False
    Current temp: 75.062C @ 01:59 PM - Switch Slow Cooker Switch is False
    Current temp: 75.062C @ 02:00 PM - Switch Slow Cooker Switch is False
    ...
    Current temp: 74.687C @ 07:50 PM - Switch Slow Cooker Switch is True
    Current temp: 74.75C @ 07:51 PM - Switch Slow Cooker Switch is True
    Turning Slow Cooker Switch off
    Timer 360 mins reached. Switch Slow Cooker Switch is now off
    Average temperature was 74.8357018545 with a 30 second accuracy

Troubleshooting:
----------------
* Q: My switch isn't found but I can see it in the WeMo app.

A: Try increasing the [discovery timer](https://github.com/detobate/sous-wemo/blob/master/souswemo.py#L79)

* Q: It can't find my temperature probe.

A: Make sure your probe shows up in: ``/sys/bus/w1/devices/``.  If not, check you've added `dtoverlay=w1-gpio` to your `/boot/config.txt`


Extra notes:
------------
- Accuracy value of 30 seconds appears to produce a deviation of ± approx. 0.7C in my slow cooker set on low.
