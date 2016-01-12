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

    ./souswemo.py 'Slow Cooker' 60C 120

Requirements:
-------------
* [DS18B20](https://www.adafruit.com/search?q=DS18B20) One Wire temperature probe. (or other probes supported by the [w1thermsensor](https://github.com/timofurrer/w1thermsensor) Python module)
* A GPIO Interface, such as on a RaspberryPi or Beaglebone. [VirtGPIO](https://github.com/BLavery/virtual-GPIO) may work but hasn't been tested.
* Python2.7 and modules listed in [requirements.txt](https://raw.githubusercontent.com/detobate/sous-wemo/master/requirements.txt)
