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
* [DS18B20](https://www.adafruit.com/search?q=DS18B20) One Wire temperature probe. (or other probes supported by the [w1thermsensor](https://github.com/timofurrer/w1thermsensor) Python module)
Follow [these](http://www.modmypi.com/blog/ds18b20-one-wire-digital-temperature-sensor-and-the-raspberry-pi) instructions if using a RaspberryPi.
* A GPIO Interface, such as on a RaspberryPi or Beaglebone. [VirtGPIO](https://github.com/BLavery/virtual-GPIO) may also work but hasn't been tested.
* Python2.6 and modules listed in [requirements.txt](https://raw.githubusercontent.com/detobate/sous-wemo/master/requirements.txt)


Example:
--------

    ./souswemo.py 'Slow Cooker' 60C 1
    Finding WeMo switches
    Turning Slow Cooker on
    Heating up. Current temp: 60
    Device on switch Slow Cooker is at target temperature 60C
    Turning Slow Cooker off
    Press Enter to start the 1 minute timer
    Current temp: 60C @ 05:23 PM - Switch Slow Cooker is False

    Timer started, start time: 05:23 PM

    Current temp: 61C @ 05:24 PM - Switch Slow Cooker is False
    Current temp: 63C @ 05:24 PM - Switch Slow Cooker is False
    Current temp: 60C @ 05:24 PM - Switch Slow Cooker is False
    Current temp: 57C @ 05:24 PM - Switch Slow Cooker is False
    Turning Slow Cooker on
    Current temp: 61C @ 05:25 PM - Switch Slow Cooker is True
    Turning Slow Cooker off
    Switch is already off
    Timer 1 mins reached. Switch Slow Cooker is now off
    Average temperature was 58 with a 15 second accuracy


Troubleshooting:
----------------
Q: My switch isn't found but I can see it in the WeMo app.

A: Try increasing the [discovery timer](https://github.com/detobate/sous-wemo/blob/master/souswemo.py#L84)

Q: It can't find my temperature probe.

A: Make sure your probe shows up in: ``/sys/bus/w1/devices/``.  If not, check you've added `dtoverlay=w1-gpio` to your `/boot/config.txt`
