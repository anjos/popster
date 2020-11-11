#!/usr/bin/env python

import os
import sys
import hashlib
import collections
import itertools

import logging

logger = logging.getLogger(__name__)

import tqdm

# from https://stackoverflow.com/questions/748675/finding-duplicate-files-and-removing-them


def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash=hashlib.sha256):
    hashobj = hash()
    file_object = open(filename, "rb")

    if first_chunk_only:
        hashobj.update(file_object.read(1024))
    else:
        for chunk in chunk_reader(file_object):
            hashobj.update(chunk)
    hashed = hashobj.digest()

    file_object.close()
    return hashed


def check_duplicates(paths, hash=hashlib.sha256):
    """Checks for duplicates in multiple paths, returns a list of duplicates"""

    assert isinstance(paths, (tuple, list))

    # dict of size_in_bytes: [full_path_to_file1, full_path_to_file2, ]
    hashes_by_size = collections.defaultdict(list)

    # dict of (hash1k, size_in_bytes): [full_path_to_file1, full_path_to_file2, ]
    hashes_on_1k = collections.defaultdict(list)

    hashes_full = {}  # dict of full_file_hash: full_path_to_file_string

    for path in paths:
        for dirpath, dirnames, filenames in tqdm.tqdm(
            os.walk(path),
            desc="scanning directories",
            unit="",
            leave=True,
            disable=None,
        ):
            # get all files that have the same size -
            # they are the collision candidates
            for filename in tqdm.tqdm(
                sorted(filenames),
                desc="hashing file sizes",
                unit="",
                leave=False,
                disable=None,
            ):
                full_path = os.path.join(dirpath, filename)
                try:
                    # if the target is a symlink (soft one), this will
                    # dereference it - change the value to the actual target
                    # file
                    full_path = os.path.realpath(full_path)
                    file_size = os.path.getsize(full_path)
                    hashes_by_size[file_size].append(full_path)
                except (OSError,):
                    # not accessible (permissions, etc) - pass on
                    continue

    # For all files with the same file size, get their hash on the 1st 1024
    # bytes only
    for size_in_bytes, files in tqdm.tqdm(
        hashes_by_size.items(),
        desc="hashing first kb",
        unit="",
        leave=True,
        disable=None,
    ):
        if len(files) < 2:
            # this file size is unique, no need to spend CPU cycles on it
            continue

        for filename in tqdm.tqdm(
            files,
            desc="files",
            unit="",
            leave=False,
            disable=None,
        ):
            try:
                small_hash = get_hash(filename, first_chunk_only=True)
                # the key is the hash on the first 1024 bytes plus the size -
                # to avoid collisions on equal hashes in the first part of the
                # file credits to @Futal for the optimization
                hashes_on_1k[(small_hash, size_in_bytes)].append(filename)
            except (OSError,):
                # the file access might've changed till the exec point got here
                continue

    # For all files with the hash on the 1st 1024 bytes, get their hash on the
    # full file - collisions will be duplicates
    duplicates = {}
    for __, files_list in tqdm.tqdm(
        hashes_on_1k.items(),
        desc="full hashing",
        unit="",
        leave=True,
        disable=None,
    ):
        if len(files_list) < 2:
            # this hash of first 1k file bytes is unique, no need to spend cpu
            # cycles on it
            continue

        for filename in tqdm.tqdm(
            files_list,
            desc="files",
            unit="",
            leave=False,
            disable=None,
        ):
            try:
                full_hash = get_hash(filename, first_chunk_only=False)
                duplicate = hashes_full.get(full_hash)
                if duplicate:
                    duplicates.setdefault(full_hash, set()).update(
                        (
                            os.path.realpath(filename),
                            os.path.realpath(duplicate),
                        )
                    )
                    logger.debug(f"Duplicate: {filename} and {duplicate}")
                else:
                    hashes_full[full_hash] = filename
            except (OSError,):
                # the file access might've changed till the exec point got here
                continue

    return list(duplicates.values())


def recommend_action(duplicates):
    """Lists recommendations for removal/checks based on filenames

    This function will input a list of sets containing duplicates found with
    :py:func:`check_duplicates`.  For each set in the list, it will split the
    set in two parts with items that can be safely erased (backups) and items
    that require manual organization (e.g. different basenames for the same
    file contents).

    Parameters
    ==========

    duplicates : list of set
        A list of sets with the duplicates


    Returns
    =======

    erase : list
        A list of files that can be safely removed as these are backups

    check : list of set
        A list of sets containing files that need to be manually checked

    """

    def _backup_of(path):
        name, extension = os.path.splitext(path)
        return name.rstrip("~") + extension

    def _all_equal(iterable):
        g = itertools.groupby(iterable)
        return next(g, True) and not next(g, False)

    erase = []  # items that are backups and could be erased from the disk
    check = []  # items that should be checked as they have different names

    for items in duplicates:
        keep = []
        for filename in sorted(items):  # backups will appear last
            if filename.endswith(".aae"):  # too many are similar to remove them
                continue
            if _backup_of(filename) not in keep:
                keep.append(filename)
            else:
                erase.append(filename)
                # if a ".aae" file exists, also remove that one
                aae = os.path.splitext(filename)[0] + ".aae"
                if os.path.exists(aae):
                    erase.append(aae)

        # if base directories are the same, then preserve the copy with the
        # shortest name as a rule of thumb.
        if _all_equal([os.path.dirname(k) for k in keep]):
            s = sorted(keep, key=lambda x: len(x))
            for i in s[1:]:
                erase.append(i)
                aae = os.path.splitext(i)[0] + ".aae"
                if os.path.exists(aae):
                    erase.append(aae)
            logger.debug(f"keeping {s[0]} (out of {len(s)})")
            keep = []  #forget the first entry

        if len(keep) >= 2:
            # there are duplicates with different names
            check.append(keep)

    return erase, check
