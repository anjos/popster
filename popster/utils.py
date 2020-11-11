#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""General utilities for image processing and filtering"""

import os
import sys
import json
import time
import shutil
import subprocess

import logging

logger = logging.getLogger(__name__)


def retrieve_json_secret(key):
    """Retrieves a secret in JSON format from password-store"""

    logger.info(f"Retrieving '{key}' from password-store...", key)
    passbin = shutil.which("pass")
    if passbin is None:
        raise RuntimeError(
            f"The program 'pass' should be installed and "
            f"on your $PATH so I can retrieve {key} from the password-store"
        )
    else:
        logger.debug(f"Using 'pass' from {passbin} to retrieve '{key}'...")
    p = subprocess.Popen(
        [passbin, "show", key], stdin=sys.stdin, stdout=subprocess.PIPE
    )
    return json.loads(p.communicate()[0].strip())


_INTERVALS = (
    ("weeks", 604800),  # 60 * 60 * 24 * 7
    ("days", 86400),  # 60 * 60 * 24
    ("hours", 3600),  # 60 * 60
    ("minutes", 60),
    ("seconds", 1),
)


def human_time(seconds, granularity=2):
    '''Returns a human readable time string like "1 day, 2 hours"'''

    result = []

    for name, count in _INTERVALS:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip("s")
            result.append(f"{value:d} {name}")
        else:
            # Add a blank if we're in the middle of other values
            if len(result) > 0:
                result.append(None)

    if not result:
        if seconds < 1.0:
            return f"{seconds:.2f} seconds"
        else:
            if seconds == 1:
                return "1 second"
            else:
                return f"{seconds:d} seconds"

    return ", ".join([x for x in result[:granularity] if x is not None])


def run_cmdline(cmd, env=None, mask=None):
    """Runs a command on a environment, logs output and reports status


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

    """

    if env is None:
        env = os.environ

    cmd_log = cmd
    if mask:
        cmd_log = copy.copy(cmd)
        for k in range(mask, len(cmd)):
            cmd_log[k] = "*" * len(cmd_log[k])
    logger.info(f"$ {' '.join(cmd_log)}")

    start = time.time()
    out = b""

    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env
    )

    chunk_size = 1 << 13
    lineno = 0
    for chunk in iter(lambda: p.stdout.read(chunk_size), b""):
        decoded = chunk.decode()
        while "\n" in decoded:
            pos = decoded.index("\n")
            logger.debug(f"{lineno:03d}: {decoded[:pos]}")
            decoded = decoded[pos + 1 :]
            lineno += 1
        out += chunk

    if p.wait() != 0:
        logger.error(f"Command output is:\n{out.decode()}")
        raise RuntimeError(
            f"command `{' '.join(cmd_log)}' exited with "
            f"error state ({p.returncode:d})"
        )

    total = time.time() - start

    logger.debug(f"command took {human_time(total)}")

    out = out.decode()

    return out


def heic_to_jpeg(sips, path, quality="best"):
    """Converts input image from HEIF format to JPEG, preserving all metadata

    This function uses the command line utility ``sips``, which is unfortunately
    only available on macOS.

    Parameters:


      sips (str): Path to the ``sips`` command-line application, to be obtained
        with :py:func:`shutil.which`.

      path (str): The path leading to the HEIF file (with either ``.heic`` or
        ``.heif`` extension)

      quality (:py:class:`str`, Optional): One of
        ``low|normal|high|best|<percent>`` (in doubt, consult the
        ``formatOptions`` entry in ``man sips`` on your macOS system.  The
        current default is ``best``.


    Returns:

      str: Path to the output file generated

    """

    input_dirname = os.path.dirname(path)
    input_filename = os.path.basename(path)
    input_basename = os.path.splitext(input_filename)[0]

    output_extension = ".JPG"
    if input_basename.islower():
        output_extension = ".jpg"

    output_path = os.path.join(input_dirname, input_basename + output_extension)

    if os.path.exists(output_path):
        logger.warn(f"file '{output_path}' already exists - " \
                f"backing-up and overwriting...")
        backup = os.path.join(
            input_dirname, input_basename + "~" + output_extension
        )
        if os.path.exists(backup):
            os.unlink(backup)
            logger.info(f"removed old backup file '{backup}'")
        shutil.move(output_path, backup)
        logger.info(f"[backup] '{output_path}' -> '{backup}'")

    cmd = [
        sips,
        "--setProperty",
        "format",
        "jpeg",
        path,
        "-s",
        "formatOptions",
        "best",
        "--out",
        output_path,
    ]
    run_cmdline(cmd)

    # setup destination file to have the same access/modification times as source
    stat = os.stat(path)
    os.utime(output_path, (stat.st_atime, stat.st_mtime))

    return output_path


def files_match(p1, p2):
    """Returns ``True`` if files pointed by path ``p1`` and ``p2`` have equal
    contents.  Otherwise, ``False``.
    """

    __import__('ipdb').set_trace()
    pass
