---------
 Popster
---------

This is Popster, a photo importer and sorter written in Python. I wrote it to
easily import photos from my cameras when I pop the SD card into the slot
reader of my NAS (QNAP-451A).


Installation
------------

The library is preconfigured to work for my system. You may need to edit it to
make it work for yours. Otherwise, you can just::

  $ python bootstrap.py
  $ ./bin/buildout

These two commands should leave you with a functional environment. If one of
the dependencies fails to install (such as Pillow, for example), install them
using your preferred package manager and then start from scratch.


Usage
-----

There is a single program that you can launch as a daemon on your system::

  $ ./bin/popin --help

And a complete help message will be displayed.
