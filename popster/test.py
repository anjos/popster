#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Test units'''

import os
import time
import shutil
import datetime
import tempfile
import pkg_resources

import nose.tools

from .sorter import read_creation_date, copy, rcopy, DateReadoutError, Sorter


def data_path(f=None):
  '''Returns a path to a data item inside the package'''

  obj = 'data' if not f else os.path.join('data', f)
  return pkg_resources.resource_filename(__name__, obj)


def test_jpeg_readout():

  # Tests one extract the proper exif tag from a jpeg file

  date = read_creation_date(data_path('img_with_exif.jpg'))
  assert date == datetime.datetime(2003, 12, 14, 12, 1, 44)


def test_movie_readout():

  # Tests one extract the proper exif tag from a jpeg file

  date = read_creation_date(data_path('mp4.mp4'))
  assert date == datetime.datetime(2005, 10, 28, 17, 46, 46)


@nose.tools.raises(DateReadoutError)
def test_exif_failure():

  # Tests it raises a proper exception when the jpeg file has no exif info
  read_creation_date(data_path('img_without_exif.jpg'))


def test_move():

  # Tests if can organize at least the sample photo

  # Temporary setup
  src = data_path('img_with_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, base, dst, fmt, move=True, dry=False)
    assert os.path.exists(result)
    assert not os.path.exists(subfolder) #removed
    assert os.path.exists(base) #not removed


@nose.tools.raises(DateReadoutError)
def test_move_fails():

  # Tests if can correctly detect moving fails

  # Temporary setup
  src = data_path('img_without_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, base, dst, fmt, move=True, dry=False)
    assert os.path.exists(result)
    assert not os.path.exists(subfolder) #removed
    assert os.path.exists(base) #not removed


def test_move_dry():

  # Tests if can organize at least the sample photo

  # Temporary setup
  src = data_path('img_with_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, base, dst, fmt, move=True, dry=True)
    assert os.path.exists(subfolder) #removed
    assert not os.path.exists(result)


def test_copy():

  # Tests if can organize at least the sample photo

  # Temporary setup
  src = data_path('img_with_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, base, dst, fmt, move=False, dry=False)
    assert os.path.exists(result)
    assert os.path.exists(subfolder)


def test_copy_same():

  # Tests if can organize at least the sample photo

  # Temporary setup
  src = data_path('img_with_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result1 = copy(src, base, dst, fmt, move=False, dry=False)
    assert os.path.exists(result1)
    assert os.path.exists(subfolder)
    # do it again
    result2 = copy(src, base, dst, fmt, move=False, dry=False)
    assert os.path.exists(result2)
    assert result1 != result2
    assert result2.endswith('+.jpg')
    assert os.path.exists(subfolder)


@nose.tools.raises(DateReadoutError)
def test_copy_fails():

  # Tests if can organize at least the sample photo

  # Temporary setup
  src = data_path('img_without_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, base, dst, fmt, move=False, dry=False)
    assert os.path.exists(result)
    assert os.path.exists(subfolder)


def test_copy_dry():

  # Tests if can organize at least the sample photo

  # Temporary setup
  src = data_path('img_with_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, base, dst, fmt, move=False, dry=True)
    assert os.path.exists(subfolder)
    assert not os.path.exists(result)


def test_move_many():

  # Tests if we can move a whole ensemble of files

  data = data_path()
  fmt = '%Y/%B/%d.%m.%Y'

  # Ground truth
  bad_src = ['img_without_exif.jpg']
  bad_src = [os.path.join(os.path.basename(data), k) for k in bad_src]
  good_src = [
      'img_with_exif.jpg',
      'mp4.mp4',
      ]
  good_src = [os.path.join(os.path.basename(data), k) for k in good_src]
  good_dst = [
      os.path.join('2003', 'december', '14.12.2003', 'img_with_exif.jpg'),
      os.path.join('2005', 'october', '28.10.2005', 'mp4.mp4'),
      ]

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:
    src = os.path.join(base, os.path.basename(data))
    shutil.copytree(data, src)
    good, bad = rcopy(base, dst, fmt, move=True, dry=False)
    bad_full = [os.path.join(base, k) for k in bad_src]
    assert sorted(bad_full) == sorted(bad)
    for k in bad_full:
      assert os.path.exists(k), '%r does not exist' % k
    good_full = [os.path.join(dst, k) for k in good_dst]
    assert sorted(good_full) == sorted(good)
    for k in good_full:
      assert os.path.exists(k), '%r does not exist' % k
    old_good_full = [os.path.join(base, k) for k in good_src]
    for k in old_good_full:
      assert not os.path.exists(k), '%r still exists' % k


def test_move_all():

  # Tests if we can move a whole ensemble of files and that the source
  # directory is correctly removed

  data = data_path()
  fmt = '%Y/%B/%d.%m.%Y'

  # Ground truth
  bad_src = ['img_without_exif.jpg']
  bad_src = [os.path.join(os.path.basename(data), k) for k in bad_src]
  good_src = [
      'img_with_exif.jpg',
      'mp4.mp4',
      ]
  good_src = [os.path.join(os.path.basename(data), k) for k in good_src]
  good_dst = [
      os.path.join('2003', 'december', '14.12.2003', 'img_with_exif.jpg'),
      os.path.join('2005', 'october', '28.10.2005', 'mp4.mp4'),
      ]

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:
    src = os.path.join(base, os.path.basename(data))
    shutil.copytree(data, src)

    # remove unwanted files
    for k in bad_src:
      os.unlink(os.path.join(base, k))

    good, bad = rcopy(base, dst, fmt, move=True, dry=False)

    assert len(bad) == 0

    good_full = [os.path.join(dst, k) for k in good_dst]
    assert sorted(good_full) == sorted(good)
    for k in good_full:
      assert os.path.exists(k), '%r does not exist' % k
    old_good_full = [os.path.join(base, k) for k in good_src]
    for k in old_good_full:
      assert not os.path.exists(k), '%r still exists' % k

    # asserts the original directory is removed up to, but excluding, src
    assert not os.path.exists(src)
    assert os.path.exists(base)


def test_watch():

  # Tests if we can move a whole ensemble of files and that the source
  # directory is correctly removed

  data = data_path()
  fmt = '%Y/%B/%d.%m.%Y'

  # Ground truth
  bad_src = ['img_without_exif.jpg']
  bad_src = [os.path.join(os.path.basename(data), k) for k in bad_src]
  good_src = [
      'img_with_exif.jpg',
      'mp4.mp4',
      ]
  good_src = [os.path.join(os.path.basename(data), k) for k in good_src]
  good_dst = [
      os.path.join('2003', 'december', '14.12.2003', 'img_with_exif.jpg'),
      os.path.join('2005', 'october', '28.10.2005', 'mp4.mp4'),
      ]

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:

    sorter = Sorter(base, dst, fmt, move=True, dry=False, email=False,
        idleness=10)
    sorter.start()

    # simulates copying (creating) data into the base directory
    src = os.path.join(base, os.path.basename(data))
    shutil.copytree(data, src)

    time.sleep(1)
    sorter.stop()
    sorter.join()

    bad_full = [os.path.join(base, k) for k in bad_src]
    for k in bad_full:
      assert os.path.exists(k), '%r does not exist' % k
    good_full = [os.path.join(dst, k) for k in good_dst]
    for k in good_full:
      assert os.path.exists(k), '%r does not exist' % k
    old_good_full = [os.path.join(base, k) for k in good_src]
    for k in old_good_full:
      assert not os.path.exists(k), '%r still exists' % k

    assert os.path.exists(src)
    assert os.path.exists(base)


def test_watch_move():

  # Tests if we can move a whole ensemble of files and that the source
  # directory is correctly removed - in this variant, we move the files into
  # the "watched" directory instead of copying them, to make sure we don't need
  # another "on_move" method in our Handler class.

  data = data_path()
  fmt = '%Y/%B/%d.%m.%Y'

  # Ground truth
  bad_src = ['img_without_exif.jpg']
  bad_src = [os.path.join(os.path.basename(data), k) for k in bad_src]
  good_src = [
      'img_with_exif.jpg',
      'mp4.mp4',
      ]
  good_src = [os.path.join(os.path.basename(data), k) for k in good_src]
  good_dst = [
      os.path.join('2003', 'december', '14.12.2003', 'img_with_exif.jpg'),
      os.path.join('2005', 'october', '28.10.2005', 'mp4.mp4'),
      ]

  with tempfile.TemporaryDirectory() as start, \
      tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:

    sorter = Sorter(base, dst, fmt, move=True, dry=False, email=False,
        idleness=10)
    sorter.start()

    # simulates moving data into the base directory
    starting_point = os.path.join(start, os.path.basename(data))
    shutil.copytree(data, starting_point)
    shutil.move(starting_point, base)

    time.sleep(1)
    sorter.stop()
    sorter.join()

    bad_full = [os.path.join(base, k) for k in bad_src]
    for k in bad_full:
      assert os.path.exists(k), '%r does not exist' % k
    good_full = [os.path.join(dst, k) for k in good_dst]
    for k in good_full:
      assert os.path.exists(k), '%r does not exist' % k
    old_good_full = [os.path.join(base, k) for k in good_src]
    for k in old_good_full:
      assert not os.path.exists(k), '%r still exists' % k

    assert not os.path.exists(starting_point)
    assert os.path.exists(os.path.join(base, os.path.basename(data)))
    assert os.path.exists(base)


def test_start_with_files():

  # Tests if we can move a whole ensemble of files and that the source
  # directory is correctly removed

  data = data_path()
  fmt = '%Y/%B/%d.%m.%Y'

  # Ground truth
  bad_src = ['img_without_exif.jpg']
  bad_src = [os.path.join(os.path.basename(data), k) for k in bad_src]
  good_src = [
      'img_with_exif.jpg',
      'mp4.mp4',
      ]
  good_src = [os.path.join(os.path.basename(data), k) for k in good_src]
  good_dst = [
      os.path.join('2003', 'december', '14.12.2003', 'img_with_exif.jpg'),
      os.path.join('2005', 'october', '28.10.2005', 'mp4.mp4'),
      ]

  with tempfile.TemporaryDirectory() as base, \
      tempfile.TemporaryDirectory() as dst:

    # simulates moving data into the base directory before watchdog is started
    src = os.path.join(base, os.path.basename(data))
    shutil.copytree(data, src)

    # remove unwanted files
    for k in bad_src:
      os.unlink(os.path.join(base, k))

    sorter = Sorter(base, dst, fmt, move=True, dry=False, email=False,
        idleness=10)
    sorter.start()

    time.sleep(1)
    sorter.stop()
    sorter.join()

    good_full = [os.path.join(dst, k) for k in good_dst]
    for k in good_full:
      assert os.path.exists(k), '%r does not exist' % k
    old_good_full = [os.path.join(base, k) for k in good_src]
    for k in old_good_full:
      assert not os.path.exists(k), '%r still exists' % k

    # asserts the original directory is removed up to, but excluding, src
    assert not os.path.exists(src)
    assert os.path.exists(base)
