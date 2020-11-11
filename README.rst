.. image:: https://travis-ci.org/anjos/popster.svg?branch=master
   :target: https://travis-ci.org/anjos/popster
.. image:: https://img.shields.io/docker/pulls/anjos/popster.svg
   :target: https://hub.docker.com/r/anjos/popster/

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

Where ``x.y`` can be either ``2.7`` or ``3.6``. Once the environment is
installed, activate it to be able to call binaries::

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

  $ source activate popster-dev
  (popster-dev) $ buildout

This command should leave you with a functional environment.


Testing
=======

To test the package, run the following::

  (popster-dev) $ ./bin/nosetests -sv --with-coverage --cover-package=popster


Conda Builds
============

Building dependencies requires you install ``conda-build``. Do the following to
prepare::

  $ conda activate base
  (base) $ conda install conda-build anaconda-client

Then, you can build dependencies one by one, in order::

  $ vi ./scripts/conda-build-all.sh #comment/uncomment what to compile
  $ conda activate base
  (base) $ ./scripts/conda-build-all.sh
  ...
  (base) $ #now, execute the lines of interest


Anaconda Uploads
================

To upload all built dependencies (so you don't have to re-build them
everytime), do::

  $ anaconda login
  # enter credentials
  $ anaconda upload <conda-bld>/*-64/mediainfo-*.tar.bz2
  $ anaconda upload <conda-bld>/*-64/pymediainfo-*.tar.bz2
  $ anaconda upload <conda-bld>/noarch/{exifread,popster}-*.tar.bz2


Docker Image Building
=====================

To build a readily deployable docker image, do::

  $ docker build --rm -t anjos/popster:latest .
  $ #upload it like this:
  $ docker push anjos/popster:latest


.. note::

   Before running the above command, make sure to tag this package
   appropriately and to build and deploy conda packages for such a release.
   Also build the equivalent version-named container using ``-t
   anjos/popster:vX.Y.Z``.


Deployment
----------

QNAP has a proprietary packaging format for native applications called QPKG_.
While it allows one to create apps that are directly installable using QNAP's
App Center, it also ties in the running environment (mostly libc's
dependencies) for the current OS. This implies applications need to be
re-packaged at every major OS release. It may also bring conflicts with Conda's
default channel ABIs.

Instead of doing so, I opted for a deployment based on Docker containers. The
main advantages of this approach is that containers are (almost) OS independent
and there is a huge source of information and resources for building container
images on the internet.

To deploy popster, just download the released image at DockerHub_ and create a
container through Container Station. The container starts the built-in
``watch`` application that moves images/movies from one directory to another,
for later curation. I typically just mount media files (set this in "Advanced
Settings" -> "Shared folders") to be organized inside ``/imported`` and move
them to ``/organized`` for later curation. The run command I typically use is
this::

  # choose entrypoint to be "watch"
  -vv --idleness=30 --source=/imported --dest=/organized --no-date-path="Missing-Date" --email --username="your.username@gmail.com" --password="create-an-app-password-for-gmail"

If you'd like to use Gmail for sending e-mails about latest activity, just make
sure to set the ``--email`` flag and set your username and specific-app
password (to avoid 2-factor authentication). ``popster`` should handle this
flawlessly. Other e-mail providers should also be reacheable in the same way.


.. Place your references after this line
.. _conda: http://conda.pydata.org/miniconda.html
.. _mediainfo: https://mediaarea.net/en/MediaInfo
.. _qpkg: https://wiki.qnap.com/wiki/QPKG_Development_Guidelines
.. _dockerhub: https://hub.docker.com/r/anjos/popster/
