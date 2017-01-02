#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""All functions and classes that can sort photos from one folder to another"""


import os
import stat
import errno
import shutil
import datetime
import logging
logger = logging.getLogger(__name__)
from PIL import Image, ExifTags


EXTENSIONS=[
    '.jpg',
    '.avi',
    '.mp4',
    ]
EXTENSIONS.__doc__ = "List of extensions supported by this program (lower-case)"


def read_date(path):
  """Retrieves the original file date"""

  date = Image.open(path)._getexif()[36867]

  # convert to python datetime
  import ipdb; ipdb.set_trace()


def make_dirs(path, name, dry):
  """Creates a directory preserving owner, group and parent permissions


  Parameters:

    path (str): Base path where the directory will be created
    name (str): The name of the directory to create
    dry (bool): If set to ``True``, then it will not copy anything, just log.


  Returns:

    str: The equivalent of ``os.path.join(path, name)``.

  """

  retval = os.path.join(path, name)

  # safe creates the directory
  if (not os.path.exists(retval)) and (not dry):
    info = os.stat(path)
    try:
      os.makedirs(retval, info.st_mode)
      basedir = name.split(os.sep)[0]
      for root, dirs, files in os.walk(os.path.join(path, basedir)):
        for d in dirs:
          os.chown(os.path.join(root, d), info.st_uid, info.st_gid)
    except OSError as exception:
      if exception.errno != errno.EEXIST: raise
    else:
      logger.info("Created directory %s" % retval)

  return retval


def move(src, base, dst, fmt, dry=False):
  """Moves a single source file to a destination directory

  This function performs 4 distinct tasks:

    1. Determines if file has a supported extension, otherwise ignores it
    2. Figures out when the file was produced
    3. Moves file to destination directory
    4. Checks originating directory - if empty, suppress it up to ``base``


  Parameters:

    src (str): The path leading to the source object that must exist

    base (str): The path leading to the base directory that is being monitored.
      This value is provided so we don't accidentally erase it.

    dst (str): A path leading to the base destination directory where to store
      pictures. If the path does not exist, it will be created.

    fmt (str): A string containing date formatters for a folder structure that
      will be added to destination folder, prefixing the files copied.

    dry (bool): If set to ``True``, then it will not copy anything, just log.

  """

  # 1. determines if file is something we need to take care of
  if os.path.splitext(src)[1].lower() not in EXTENSIONS:
    logger.debug("Ignoring %s (not in extension list)" % src)
    return

  # 2. figures out when the file was produced
  date = read_date(src)

  # 3. move file to destination directory
  dst_dirname = os.path.join(dst, date.strftime(fmt).lower())
  dst_filename = os.path.join(dist_dirname, os.path.basename(src).lower())
  dst_path = make_dirs(dst_dirname, dst_filename, dry)
  if not dry:
    shutil.move(src, dst_name)
  logger.info("%s -> %s" % (src, dst_name))

  # 4. check originating directory - if empty, suppress it up to ``base``
  base = os.path.realpath(base)
  src = os.path.dirname(os.path.realpath(src))
  while (not os.listdir(src)) and (not os.path.samefile(src, base)):
    if not dry:
      os.rmdir(src)
    logger.info("rmdir %s" % src)
    src = os.path.dirname(src)
