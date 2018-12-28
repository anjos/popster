#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''General utilities for image processing and filtering'''

import os
import time
import shutil
import subprocess

import logging
logger = logging.getLogger(__name__)


def which(program):
  '''Pythonic version of the `which` command-line application'''

  def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

  fpath, fname = os.path.split(program)
  if fpath:
    if is_exe(program): return program
  else:
    for path in os.environ["PATH"].split(os.pathsep):
      exe_file = os.path.join(path, program)
      if is_exe(exe_file): return exe_file

  return None


_INTERVALS = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )

def human_time(seconds, granularity=2):
  '''Returns a human readable time string like "1 day, 2 hours"'''

  result = []

  for name, count in _INTERVALS:
    value = seconds // count
    if value:
      seconds -= value * count
      if value == 1:
        name = name.rstrip('s')
      result.append("{} {}".format(int(value), name))
    else:
      # Add a blank if we're in the middle of other values
      if len(result) > 0:
        result.append(None)

  if not result:
    if seconds < 1.0:
      return '%.2f seconds' % seconds
    else:
      if seconds == 1:
        return '1 second'
      else:
        return '%d seconds' % seconds

  return ', '.join([x for x in result[:granularity] if x is not None])


def run_cmdline(cmd, env=None, mask=None):
  '''Runs a command on a environment, logs output and reports status


  Parameters:

    cmd (list): The command to run, with parameters separated on a list

    env (dict, Optional): Environment to use for running the program on. If not
      set, use :py:obj:`os.environ`.

    mask (int, Optional): If set to a value that is different than ``None``,
      then we replace everything from the cmd list index ``[mask:]`` by
      asterisks.  This may be imoprtant to avoid passwords or keys to be shown
      on the screen or sent via email.


  Returns:

    str: The standard output and error of the command being executed

  '''

  if env is None: env = os.environ

  cmd_log = cmd
  if mask:
    cmd_log = copy.copy(cmd)
    for k in range(mask, len(cmd)):
      cmd_log[k] = '*' * len(cmd_log[k])
  logger.info('$ %s' % ' '.join(cmd_log))

  start = time.time()
  out = b''

  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
      env=env)

  chunk_size = 1 << 13
  lineno = 0
  for chunk in iter(lambda: p.stdout.read(chunk_size), b''):
    decoded = chunk.decode()
    while '\n' in decoded:
      pos = decoded.index('\n')
      logger.debug('%03d: %s' % (lineno, decoded[:pos]))
      decoded = decoded[pos+1:]
      lineno += 1
    out += chunk

  if p.wait() != 0:
    logger.error('Command output is:\n%s', out.decode())
    raise RuntimeError("command `%s' exited with error state (%d)" % \
        (' '.join(cmd_log), p.returncode))

  total = time.time() - start

  logger.debug('command took %s' % human_time(total))

  out = out.decode()

  return out


def heic_to_jpeg(sips, path, quality='best'):
  '''Converts input image from HEIF format to JPEG, preserving all metadata

  This function uses the command line utility ``sips``, which is unfortunately
  only available on macOS.

  Parameters:


    sips (str): Path to the ``sips`` command-line application, to be obtained
      with :py:func:`which`.

    path (str): The path leading to the HEIF file (with either ``.heic`` or
      ``.heif`` extension)

    quality (:py:class:`str`, Optional): One of
      ``low|normal|high|best|<percent>`` (in doubt, consult the
      ``formatOptions`` entry in ``man sips`` on your macOS system.  The
      current default is ``best``.


  Returns:

    str: Path to the output file generated

  '''

  input_dirname = os.path.dirname(path)
  input_filename = os.path.basename(path)
  input_basename = os.path.splitext(input_filename)[0]

  output_extension = '.JPG'
  if input_basename.islower(): output_extension = '.jpg'

  output_path = os.path.join(input_dirname, input_basename + output_extension)

  if os.path.exists(output_path):
    logger.warn('file "%s" already exists - backing-up and overwriting...',
        output_path)
    backup = os.path.join(input_dirname, input_basename + '~' + output_extension)
    if os.path.exists(backup):
      os.unlink(backup)
      logger.info('removed old backup file "%s"', backup)
    shutil.move(output_path, backup)
    logger.info('[backup] "%s" -> "%s"', output_path, backup)

  cmd = [sips, '--setProperty', 'format', 'jpeg', path, '-s', 'formatOptions',
      'best', '--out', output_path]
  run_cmdline(cmd)

  # setup destination file to have the same access/modification times as source
  stat = os.stat(path)
  os.utime(output_path, (stat.st_atime, stat.st_mtime))

  return output_path
