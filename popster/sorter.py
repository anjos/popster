#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""All functions and classes that can sort photos from one folder to another"""


import os
import sys
import time
import stat
import errno
import shutil
import datetime
import platform

import logging
logger = logging.getLogger(__name__)

from PIL import Image, ExifTags
from pymediainfo import MediaInfo
import watchdog.events
import watchdog.observers
import smtplib


EXTENSIONS=[
    '.jpg',
    '.thm', #thumbnail files, with exif information (little jpg)
    '.avi', #older cameras
    '.mp4', #canon powershot g7 x mark ii
    '.mov', #iphone, powershot sx230 hs, canon eos 500d
    '.m4v', #ipod encoded clips
    ]
"""List of extensions supported by this program (lower-case)"""


def _ignore_dir(d):
  """Select directories that should be ignored"""

  return d.startswith('.') or d in ('MISC', 'CANONMSC')


def _ignore_file(path, f):
  """Select files that should be ignored"""

  if f in ('.DS_Store', '.Icon'): return True

  for p in path.split(os.sep):
    if _ignore_dir(p): return True

  return False


EMAIL_SENDER = 'Andre Anjos <andre.dos.anjos@gmail.com>'
EMAIL_RECEIVERS = [
    'Andre Anjos <andre.dos.anjos@gmail.com>',
    #'Ana Carolina Anjos <ana.carolina.anjos@gmail.com>',
    ]
"""E-mail sender and receivers for informative actions"""


FILEMASK=(stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP|stat.S_IWGRP|stat.S_IROTH|stat.S_IWOTH)
"""Mask of permissions for files to be moved"""


class DateReadoutError(IOError):
  """Exception raised in case :py:func:`read_creation_date` returns an error"""
  pass


class UnsupportedExtensionError(IOError):
  """Exception raised in case :py:func:`read_creation_date` does not support the extension on file being read"""
  pass


def setup_logger(name, verbosity):
  '''Sets up the logging of a script


  Parameters:

    name (str): The name of the logger to setup

    verbosity (int): The verbosity level to operate with. A value of ``0``
      (zero) means only errors, ``1``, errors and warnings; ``2``, errors,
      warnings and informational messages and, finally, ``3``, all types of
      messages including debugging ones.

  '''

  logger = logging.getLogger(name)
  formatter = logging.Formatter("%(name)s@%(asctime)s -- %(levelname)s: " \
      "%(message)s")

  _warn_err = logging.StreamHandler(sys.stderr)
  _warn_err.setFormatter(formatter)
  _warn_err.setLevel(logging.WARNING)

  class _InfoFilter:
    def filter(self, record): return record.levelno <= logging.INFO
  _debug_info = logging.StreamHandler(sys.stdout)
  _debug_info.setFormatter(formatter)
  _debug_info.setLevel(logging.DEBUG)
  _debug_info.addFilter(_InfoFilter())

  logger.addHandler(_debug_info)
  logger.addHandler(_warn_err)


  logger.setLevel(logging.ERROR)
  if verbosity == 1: logger.setLevel(logging.WARNING)
  elif verbosity >= 2: logger.setLevel(logging.INFO)
  elif verbosity >= 3: logger.setLevel(logging.DEBUG)

  return logger


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
    '.m4v': _video_read_creation_date,
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

  if _ignore_file(os.path.dirname(src), os.path.basename(src)):
    raise RuntimeError('ignoring file %s - explicit ignore'  % src)

  # 1. determines if file is something we need to take care of
  if os.path.splitext(src)[1].lower() not in EXTENSIONS:
    raise UnsupportedExtensionError('ignoring file %s - extension not ' \
        'supported' % src)

  # 2. figures out when the file was produced
  date = read_creation_date(src)

  # 3. move file to destination directory
  dst_dirname = date.strftime(fmt).lower()
  dst_path = _make_dirs(dst, dst_dirname, dry)
  dst_filename = os.path.join(dst, dst_dirname, os.path.basename(src).lower())

  # if a file with the same name exists, recalls myself with a "+" added to
  # the destination filename
  if os.path.exists(dst_filename):
    dst_filename,e = os.path.splitext(dst_filename)
    dst_filename += '+' + e

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

  for path, dirs, files in os.walk(base, topdown=True):
    # ignore hidden directories
    keep = []
    for d in dirs:
      if _ignore_dir(d):
        logger.info('ignoring %s...' % os.path.join(path, d))
        continue
      keep.append(d)
    dirs[:] = keep
    for f in files:
      if _ignore_file(path, f):
        logger.info('ignoring %s...' % os.path.join(path, f))
        continue
      if f.startswith('.'):
        logger.info('ignoring %s...' % os.path.join(path, f))
      try:
        good.append(copy(os.path.join(path, f), base, dst, fmt, move, dry))
      except Exception as e:
        logger.warn('could not copy/move %s to new destination: %s', path, e)
        bad.append(os.path.join(path, f))

  return good, bad


class Email(object):
  '''An object representing a message to be sent to maintainers


  Parameters:

    subject (str): The e-mail subject

    body (str): The e-mail body

    sender (str, Optional): The e-mail sender

    to (str, Optional): The e-mail receiver

  '''

  def __init__(self, subject, body, sender=EMAIL_SENDER, to=EMAIL_RECEIVERS):

    from email.mime.text import MIMEText
    self.msg = MIMEText(body)
    self.msg['Subject'] = subject
    self.sender = sender
    self.msg['From'] = self.sender
    self.to = to
    self.msg['To'] = ', '.join(self.to)


  def send(self):
    '''Sends message'''

    s = smtplib.SMTP('localhost')
    s.send_message(self.sender, self.to, self.msg.as_string())
    s.quit()


  def message(self):
    '''Returns a string representation of the message'''

    return self.msg.as_string()



class Handler(watchdog.events.PatternMatchingEventHandler):
  '''Handles file moving/copying


  Parameters:

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

  '''

  def __init__(self, base, dst, fmt, move, dry):

    super(Handler, self).__init__(
        patterns = ['*%s' % k for k in EXTENSIONS],
        ignore_patterns = [],
        ignore_directories = True,
        case_sensitive = False,
        )

    self.base = base
    self.dst = dst
    self.fmt = fmt
    self.move = move
    self.dry = dry

    # sets up a basic logger
    self.logger = watchdog.events.LoggingEventHandler()

    # cleans-up before we start to watch, sets-up good/bad lists
    self.good, self.bad = rcopy(base, dst, fmt, move, dry)
    self.last_activity = time.time()


  def on_any_event(self, event):
    '''Catch-all event handler


    Parameters:

      event (watchdog.events.FileSystemEvent): Event corresponding to the
        event that occurred with a specific file or directory being observed

    '''

    self.logger.on_any_event(event)
    self.last_activity = time.time()


  def on_created(self, event):
    '''Called when a file or directory is created


    Parameters:

      event (watchdog.events.FileSystemEvent): Event corresponding to the
        event that occurred with a specific file or directory being observed

    '''

    try:
      self.last_activity = time.time() #log before starting
      self.good.append(copy(event.src_path, self.base, self.dst, self.fmt,
        self.move, self.dry))
    except Exception as e:
      logger.warn('could not copy/move %s to new destination: %s',
          event.src_path, e)
      self.bad.append(event.src_path)
    finally:
      self.last_activity = time.time()


  def reset(self):
    '''Reset accumulated good/bad lists'''

    self.good = []
    self.bad = []
    self.last_activity = time.time()


  def needs_clearing(self):
    '''Returns ``True`` if this handler has accumulated outputs'''

    return bool(self.good or self.bad)


  def write_email(self):
    '''Composes e-mail about accumulated outputs'''

    # compose e-mail
    if not self.good:
      subject = '[orquidea/photo] %(good_len)d files may need manual intervention'
    else:
      subject = '[orquidea/photo] Organized %(good_len)d files for you'

    body = 'Hello,\n' \
        '\n' \
        'This is an automated message that summarizes actions I performed ' \
        'at folder\n %(base)s for you.\n' \
        '\n'

    if self.good:
      body += 'List of files correctly moved (%(good_len)d):\n\n'
      body += '\n'.join(self.good) + '\n\n'
    else:
      body += 'No files moved\n\n'

    if self.bad:
      body += 'List of files that could NOT be moved (%(bad_len)d):\n\n'
      body += '\n'.join(self.bad) + '\n\n'
    else:
      body += 'No files with issues\n\n'

    body += 'That is it, have a good day!\n\nYour faithul robot\n'

    body = body % dict(
        base=self.base,
        good_len=len(self.good),
        bad_len=len(self.bad),
        )

    email = Email(subject, body)
    return email


class Sorter(object):
  '''An object that can observe and sort pics from a given directory


  Parameters:

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

    email (bool): If set to ``True``, then e-mail admins about results.

    idleness (int): Time after which, we should report

  '''

  def __init__(self, base, dst, fmt, move, dry, email, idleness):

    self.observer = watchdog.observers.Observer()
    self.handler = Handler(base, dst, fmt, move, dry)
    self.email = email
    self.idleness = idleness


  def email_check(self):
    '''Checks if needs to send e-mail, of so, do it'''

    # if there seems to be activity on the handler (this means file system
    # events are still happening), then wait more
    should_check = (time.time() - self.handler.last_activity) > self.idleness
    if not should_check: return
    self.handler.last_activity = time.time()

    # if there is nothing to report, skip
    if not self.handler.needs_clearing(): return

    email = self.handler.write_email()

    if self.email:
      logger.debug(email.message())
      email.send()
    else:
      logger.info(email.message())

    self.handler.reset()


  def start(self):
    '''Runs the watchdog loop, interrupts with signal or CTRL-C'''

    self.observer.schedule(self.handler, self.handler.base, recursive=True)
    self.observer.start()


  def stop(self):
    '''Stops the sorter'''

    self.observer.stop()


  def join(self):
    '''Joins the sorting thread'''

    self.observer.join()
