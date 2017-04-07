.. image:: https://travis-ci.org/anjos/popster.svg?branch=master
   :target: https://travis-ci.org/anjos/popster

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

I advise you to install a Conda_-based environment for deployment with this
command line::

  $ conda create --override-channels -c anjos -c defaults -n popster python=x.y popster

Where ``x.y`` can be either ``2.7``, ``3.5`` or ``3.6``. Once the environment
is installed, activate it to be able to call binaries::

  $ source activate popster


Usage
-----

There is a single program that you can launch as a daemon on your system::

  $ ./bin/watch --help

And a complete help message will be displayed.


Development
-----------

I advise you to install a Conda_-based environment for development with this
command line::

  $ conda env create -f dev.yml


Build
=====

To build the project and make it ready to run, do::

  $ source activate popster
  $ buildout

This command should leave you with a functional environment.


Testing
=======

To test the package, run the following::

  $ ./bin/nosetests -sv --with-coverage --cover-package=popster


Conda Builds
============

Building dependencies requires you install ``conda-build``. Do the following to
prepare::

  $ conda install -n root conda-build anaconda-client

Then, you can build dependencies one by one, in order::

  $ conda-build deps/mediainfo
  $ for v in 2.7 3.4 3.5 3.6; do for p in deps/pymediainfo deps/argh deps/pathtools deps/watchdog deps/zc.buildout deps/ipdb conda; do conda-build $p --python=$v; done; done


Anaconda Uploads
================

To upload all built dependencies (so you don't have to re-build them
everytime), do::

  $ anaconda login
  # enter credentials
  $ anaconda upload <conda-bld>/<os>/mediainfo-*.tar.bz2
  $ anaconda upload <conda-bld>/<os>/{pymediainfo,argh,pathtools,watchdog,zc.buildout,ipdb,popster}-*.tar.bz2


.. Place your references after this line
.. _conda: http://conda.pydata.org/miniconda.html
.. _mediainfo: https://mediaarea.net/en/MediaInfo
