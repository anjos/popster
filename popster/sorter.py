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
from pymediainfo import MediaInfo


EXTENSIONS=[
    '.jpg',
    '.avi',
    '.mp4', #canon powershot g7 x mark ii
    '.mov', #iphone, powershot sx230 hs, canon eos 500d
    ]
"""List of extensions supported by this program (lower-case)"""


FILEMASK=(stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP|stat.S_IWGRP|stat.S_IROTH|stat.S_IWOTH)
"""Mask of permissions for files to be moved"""


class DateReadoutError(IOError):
  """Exception raised in case :py:func:`read_creation_date` returns an error"""
  pass


class UnsupportedExtensionError(IOError):
  """Exception raised in case :py:func:`read_creation_date` does not support the extension on file being read"""
  pass


def _jpeg_read_creation_date(path):
  """Retrieves the original creation date of the input JPEG file

  This function use the EXIF tags (DateTimeOriginal) to figure out when a file
  was originally created. If that is not available, raises an exception.


  Parameters:

    path (str): A full-path leading to the file to read the data from


  Returns:

    datetime.datetime: A standard library date-time object representing the
      time the object was created


  Raises:

    DateReadoutError: in case an error occurs trying to extract the date the
    file was produced from its metadata.

  """

  try:
    return datetime.datetime.strptime(Image.open(path)._getexif()[36867],
        '%Y:%m:%d %H:%M:%S')
  except Exception as e:
    raise DateReadoutError(str(e))


def _video_read_creation_date(path):
  """Retrieves the original creation date of the input video file

  This function use the metadata information on video files to figure out when
  the file was originally created. If that is not available, raises an
  exception.


  Parameters:

    path (str): A full-path leading to the file to read the data from


  Returns:

    datetime.datetime: A standard library date-time object representing the
    time the object was created


  Raises:

    DateReadoutError: in case an error occurs trying to extract the date the
    file was produced from its metadata.

  """

  try:
    return datetime.datetime.strptime(MediaInfo.parse(path).tracks[0].encoded_date, '%Z %Y-%m-%d %H:%M:%S')
  except Exception as e:
    raise DateReadoutError(str(e))


CREATION_DATE_READER={
    '.jpg': _jpeg_read_creation_date,
    '.thm': _jpeg_read_creation_date,
    '.avi': _video_read_creation_date,
    '.mp4': _video_read_creation_date,
    '.mov': _video_read_creation_date,
    }
"""For each supported extension, uses a specific reader for its date"""


def read_creation_date(path):
  """Retrieves the original creation date of the input file

  This function uses one of the subfunctions defined in this module to read the
  creation date of the input file. If that is not available, raises an
  exception.


  Parameters:

    path (str): A full-path leading to the file to read the data from


  Returns:

    datetime.datetime: A standard library date-time object representing the
      time the object was created


  Raises:

    DateReadoutError: in case an error occurs trying to extract the date the
    file was produced from its metadata.

    UnsupportedExtensionError: in case the file extension is unsupported by
    this procedure

  """

  try:
    return CREATION_DATE_READER[os.path.splitext(path)[1].lower()](path)
  except KeyError as e:
    ext = os.path.splitext(path)[1].lower()
    raise UnsupportedExtensionError('not support for extension "%s" in %s' \
        % (ext, path))


def _make_dirs(path, name, dry):
  """Safely creates a directory preserving owner, group and parent permissions


  Parameters:

    path (str): Base path where the directory will be created
    name (str): The name of the directory to create
    dry (bool): If set to ``True``, then it will not copy anything, just log.


  Returns:

    str: The equivalent of ``os.path.join(path, name)``.

  """

  retval = os.path.join(path, name)

  # safely creates the directory
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


def _copy_file(src, dst, move, dry):
  """Copies file and sets permissions and ownership to meet parent directory

  This function will raise an exception in case of errors.


  Parameters:

    src (str): The path leading to the source file that will be moved
    dst (str): The path with the new file name
    move (bool): If set to ``True``, move instead of copying
    dry (bool): If set to ``True``, just show what it would do

  """

  if not dry:
    if move:
      shutil.move(src, dst)
    else:
      shutil.copyfile(src, dst)
  logger.info("%s -> %s" % (src, dst))

  if not dry:
    parent = os.path.dirname(dst)
    info = os.stat(parent)
    os.chown(dst, info.st_uid, info.st_gid)
    perms = info.st_mode & FILEMASK
    os.chmod(dst, perms)
    logger.info("chmod %s %s" % (oct(perms), dst))


def copy(src, base, dst, fmt, move, dry):
  """Copies a single source file to a destination directory

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

    fmt (str): A string containing date formatters for a **folder** structure
      that will be added to destination folder, prefixing the files copied. For
      example: ``"%Y/%B/%d.%m.%Y"``. For information on date fields that be
      used, please refer to :py:func:`time.strftime`.

    move (bool): If set to `True`, move instead of copying. Otherwise, just
      copy the files

    dry (bool): If set to ``True``, then it will not copy anything, just log.


  Returns:

    str: A string object, if the file was correctly moved, pointing out
    to the path where the new file resides.


  Raises:

    DateReadoutError: in case an error occurs trying to extract the date the
    file was produced from its metadata.

    UnsupportedExtensionError: in case the file extension is unsupported by
    this procedure

  """

  # 1. determines if file is something we need to take care of
  if os.path.splitext(src)[1].lower() not in EXTENSIONS:
    logger.warn("Ignoring %s (not in extension list)" % src)
    return

  # 2. figures out when the file was produced
  date = read_creation_date(src)

  # 3. move file to destination directory
  dst_dirname = date.strftime(fmt).lower()
  dst_path = _make_dirs(dst, dst_dirname, dry)
  dst_filename = os.path.join(dst, dst_dirname, os.path.basename(src).lower())
  _copy_file(src, dst_filename, move, dry)

  # 4. check originating directory - if empty, suppress it up to ``base``
  base = os.path.realpath(base)
  src = os.path.dirname(os.path.realpath(src))
  while (not os.listdir(src)) and (not os.path.samefile(src, base)):
    if not dry:
      os.rmdir(src)
    logger.info("rmdir %s" % src)
    src = os.path.dirname(src)

  return dst_filename


def rcopy(base, dst, fmt, move, dry):
  """Recursively copies all files found under a given base directory

  This function recursively treats all files found in the source directory. It
  emits a warning when a file was found cannot be processed. It calls
  py:func:`move` to move files that match our prescription.


  Parameters:

    src (str): The path leading to the source object that must exist

    base (str): The path leading to the base directory that is being monitored.
      This value is provided so we don't accidentally erase it.

    dst (str): A path leading to the base destination directory where to store
      pictures. If the path does not exist, it will be created.

    fmt (str): A string containing date formatters for a **folder** structure
      that will be added to destination folder, prefixing the files copied. For
      example: ``"%Y/%B/%d.%m.%Y"``. For information on date fields that be
      used, please refer to :py:func:`time.strftime`.

    move (bool): If set to ``True``, move instead of copying

    dry (bool): If set to ``True``, then it will not copy anything, just log.


  Returns:

    list: A list containing the full paths of all files successfully copied to
    the destination directory. The list correspond to the **new** file
    locations.

    list: A list containing the full paths of all files that could **not** be
    copied to the destination directory. A warning is emitted for each of the
    files that could not be moved.

  """

  good, bad = [], []

  for path, dirs, files in os.walk(base, topdown=False):
    for f in files:
      try:
        good.append(copy(os.path.join(path, f), base, dst, fmt, move, dry))
      except Exception as e:
        logger.warn('could not copy/move %s to new destination: %s', path, e)
        bad.append(path)

  return good, bad
