---------
 Popster
---------

This is Popster, a photo importer and sorter written in Python. I wrote it to
easily import photos from my cameras when I pop the SD card into the slot
reader of my NAS (QNAP-451A), or via the USB port in the front.

Popster watches a given folder for changes. Such a folder is the one you use to
copy photos from your camera or SD card. In my QNAP NAS, that folder is
`/share/Download/SmartImport`. For every file that is created in this folder
(or a subfolder of that one), a function is called inside this package to:

* Check if the file is a media file that we need to import (by extension)
* Read meta-data of the file with the creation date (EXIF or other)
* Copy file to appropriate location (e.g. `/share/Pictures/DateOrganized`),
  possibly prefixed by a directory structure matching the file date


Installation
------------

Here are the installation steps to get the ball rolling on your NAS.


Conda-based Installation (optional)
===================================

I advise you to install a Conda_-based environment for development and/or
production use of this package with this command line::

  $ conda create -n popster35 --override-channels --channel=anjos --channel=defaults python=3.5 docopt pillow nose sphinx coverage pymediainfo watchdog
  $ source activate popster35 #activates the environment for usage


Build
=====

To build the project and make it ready to run, do::

  $ python bootstrap.py
  $ ./bin/buildout

These two commands should leave you with a functional environment. If one of
the dependencies fails to install (such as Pillow, for example), install them
using your preferred package manager (e.g., using Conda_ as advised above) and
then start from scratch. Use the ``python`` binary from the respective
installation to avoid issues in this step.


Testing
=======

To test the package, run the following::

  $ ./bin/nosetests -sv


Usage
-----

There is a single program that you can launch as a daemon on your system::

  $ ./bin/watch --help

And a complete help message will be displayed.


Development
-----------

Building dependencies requires you install ``conda-build``. Do the following to
prepare::

  $ conda install conda-build anaconda-client

Then, you can build dependencies one by one, in order::

  $ conda-build deps/mediainfo
  $ for v in 2.7 3.4 3.5 3.6; do for p in pymediainfo argh pathtools watchdog; do conda-build deps/$p --python=$v; done; done

To upload all built dependencies (so you don't have to re-build them
everytime), do::

  $ anaconda login
  # enter credentials
  $ anaconda upload <conda-bld>/<os>/mediainfo-*.tar.bz2
  $ anaconda upload <conda-bld>/<os>/{pymediainfo,argh,pathtools,watchdog}-*.tar.bz2


.. Place your references after this line
.. _conda: http://conda.pydata.org/miniconda.html
.. _mediainfo: https://mediaarea.net/en/MediaInfo
