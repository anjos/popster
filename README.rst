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
* Read EXIF contents of the file
* Move file to appropriate location (e.g. `/share/Pictures`), possibly prefixed
  by a directory structure matching the file date
* Erase empty directory structures in the source directory


Installation
------------

Here are the installation steps to get the ball rolling on your NAS.


Conda-based Installation (optional)
===================================

I advise you to install a Conda_-based environment for development and/or
production use of this package with this command line::

  $ conda create -n popster35 -c conda-forge python=3.5 docopt watchdog pillow


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


Usage
-----

There is a single program that you can launch as a daemon on your system::

  $ ./bin/watch --help

And a complete help message will be displayed.


.. Place your references after this line
.. _conda: http://conda.pydata.org/miniconda.html
