#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

'''Test units'''

import os
import stat
import time
import shutil
import datetime
import pkg_resources

import nose.tools

# date used for testing purposes
DUMMY_DATE = datetime.datetime(2002, 1, 26, 11, 49, 44)

# work around to get TemporaryDirectory even in Python 2.x
import six
if six.PY2:
  from .backports.tempfile import TemporaryDirectory
else:
  from tempfile import TemporaryDirectory


from .sorter import read_creation_date, copy, rcopy, make_dirs, \
    DateReadoutError, Sorter, UnsupportedExtensionError


def data_path(f=None):
  '''Returns a path to a data item inside the package'''

  obj = 'data' if not f else os.path.join('data', f)
  return pkg_resources.resource_filename(__name__, obj)


def test_jpeg_readout():

  # Tests one extract the proper exif tag from a jpeg file

  date = read_creation_date(data_path('img_with_exif.jpg'))
  nose.tools.eq_(date, datetime.datetime(2003, 12, 14, 12, 1, 44))


def test_png_readout():

  # Tests one extract the proper date from a png file

  date = read_creation_date(data_path('img_with_xmp.png'))
  nose.tools.eq_(date, datetime.datetime(2017, 8, 29, 16, 55, 32))


def test_heic_readout():

  # Tests one extract the proper date from a heic file

  date = read_creation_date(data_path('img.heic'))
  nose.tools.eq_(date, datetime.datetime(2018, 12, 22, 10, 32, 34))


def test_aae_readout():

  # Tests one extract the proper date from a aae file
  f = data_path('editing_info.aae')
  # we'll set this as the creation/modification time on the file
  # since otherwise tests won't pass on a fresh checkout of this package
  _time = time.mktime(DUMMY_DATE.timetuple())
  os.utime(f, (_time, _time))

  date = read_creation_date(data_path('editing_info.aae'))
  nose.tools.eq_(date, DUMMY_DATE)


def test_movie_readout():

  # Tests one extract the proper exif tag from a jpeg file

  date = read_creation_date(data_path('mp4.mp4'))
  nose.tools.eq_(date, datetime.datetime(2005, 10, 28, 17, 46, 46))


@nose.tools.raises(DateReadoutError)
def test_exif_failure():

  # Tests it raises a proper exception when the jpeg file has no exif info
  read_creation_date(data_path('img_without_exif.jpg'))


@nose.tools.raises(DateReadoutError)
def test_xmp_failure():

  # Tests it raises a proper exception when the jpeg file has no exif info
  read_creation_date(data_path('img_without_xmp.png'))


def test_make_dirs():

  # Tests if our make dir equivalent will correctly set permission bits on
  # created directories
  with TemporaryDirectory() as base:

    # make a temporary dir group set-bit and read/writeable to check
    # it also provides a recipe to make it work inside our own make_dirs()
    mode = stat.S_IFDIR | stat.S_ISGID | stat.S_IRWXU | stat.S_IRWXG #drwxrws---
    top = os.path.join(base, 'top')
    os.makedirs(top, mode)
    os.chmod(top, mode) # reset group set bit, others because of umask
    info = os.stat(top)
    nose.tools.eq_(oct(info.st_mode), oct(mode))
    owner_id = info.st_uid
    group_id = info.st_gid

    # our test
    make_dirs(top, 'test', dry=False) #inherit parents permissions
    test = os.path.join(top, 'test')
    info = os.stat(test)
    # checks if preserves parent mode, owner and group
    nose.tools.eq_(oct(info.st_mode), oct(mode))
    nose.tools.eq_(info.st_uid, owner_id)
    nose.tools.eq_(info.st_gid, group_id)

    # go deeper, should preserve
    make_dirs(top, 'test/a/b/c/d', dry=False) #inherit parents permissions
    test = os.path.join(top, 'test')
    info = os.stat(test)
    # checks if preserves parent mode, owner and group
    nose.tools.eq_(oct(info.st_mode), oct(mode))
    nose.tools.eq_(info.st_uid, owner_id)
    nose.tools.eq_(info.st_gid, group_id)

    test = os.path.join(top, 'test/a/b')
    info = os.stat(test)
    # checks if preserves parent mode, owner and group
    nose.tools.eq_(oct(info.st_mode), oct(mode))
    nose.tools.eq_(info.st_uid, owner_id)
    nose.tools.eq_(info.st_gid, group_id)

    test = os.path.join(top, 'test/a/b/c/d')
    info = os.stat(test)
    # checks if preserves parent mode, owner and group
    nose.tools.eq_(oct(info.st_mode), oct(mode))
    nose.tools.eq_(info.st_uid, owner_id)
    nose.tools.eq_(info.st_gid, group_id)


def test_move_jpg():

  # Tests if can organize at least the sample photo

  # Temporary setup
  src = data_path('img_with_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, dst, fmt, timestamp=False, nodate='nodate', move=True,
        dry=False)
    assert os.path.exists(result)
    assert os.path.exists(subfolder) #not removed
    assert os.path.exists(base) #not removed


def test_move_png():

  # Tests if can organize at least the sample photo

  # Temporary setup
  src = data_path('img_with_xmp.png')
  fmt = '%Y/%B/%d.%m.%Y'

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, dst, fmt, timestamp=False, nodate='nodate', move=True,
        dry=False)
    assert os.path.exists(result)
    assert os.path.exists(subfolder) #not removed
    assert os.path.exists(base) #not removed


def test_move_jpg_nodate():

  # Tests if can correctly detect moving fails

  # Temporary setup
  src = data_path('img_without_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, dst, fmt, timestamp=False, nodate='nodate', move=True,
        dry=False)
    assert os.path.exists(result)
    assert os.path.exists(subfolder) #not removed
    assert os.path.exists(base) #not removed


def test_move_png_nodate():

  # Tests if can correctly detect moving fails

  # Temporary setup
  src = data_path('img_without_xmp.png')
  fmt = '%Y/%B/%d.%m.%Y'

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, dst, fmt, timestamp=False, nodate='nodate', move=True,
        dry=False)
    assert os.path.exists(result)
    assert os.path.exists(subfolder) #not removed
    assert os.path.exists(base) #not removed


@nose.tools.raises(UnsupportedExtensionError)
def test_move_unsupported_raises():

  # Tests if can correctly detect moving fails

  # Temporary setup
  src = data_path('unsupported.txt')
  fmt = '%Y/%B/%d.%m.%Y'

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, dst, fmt, timestamp=False, nodate='nodate', move=True,
        dry=False)
    assert os.path.exists(result)
    assert os.path.exists(subfolder) #not removed
    assert os.path.exists(base) #not removed


def test_move_dry():

  # Tests if can organize at least the sample photo

  # Temporary setup
  src = data_path('img_with_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, dst, fmt, timestamp=False, nodate='nodate', move=True,
        dry=True)
    assert os.path.exists(subfolder) #removed
    assert not os.path.exists(result) #not created


def test_copy():

  # Tests if can organize at least the sample photo

  # Temporary setup
  src = data_path('img_with_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, dst, fmt, timestamp=False, nodate='nodate', move=False,
        dry=False)
    assert os.path.exists(result)
    assert os.path.exists(subfolder)


def test_copy_same():

  # Tests if can organize at least the sample photo

  # Temporary setup
  src = data_path('img_with_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result1 = copy(src, dst, fmt, timestamp=False, nodate='nodate', move=False,
        dry=False)
    assert os.path.exists(result1)
    assert os.path.exists(subfolder)
    # do it again
    result2 = copy(src, dst, fmt, timestamp=False, nodate='nodate', move=False,
        dry=False)
    assert os.path.exists(result2)
    assert result1 != result2
    assert result2.endswith('~.jpg')
    assert os.path.exists(subfolder)


def test_copy_nodate():

  # Tests if can organize at least the sample photo

  # Temporary setup
  src = data_path('img_without_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, dst, fmt, timestamp=False, nodate='nodate', move=False,
        dry=False)
    assert os.path.exists(result)
    assert os.path.exists(subfolder)


@nose.tools.raises(UnsupportedExtensionError)
def test_copy_unsupported_raises():

  # Tests if can organize at least the sample photo

  # Temporary setup
  src = data_path('unsupported.txt')
  fmt = '%Y/%B/%d.%m.%Y'

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, dst, fmt, timestamp=False, nodate='nodate', move=False,
        dry=False)
    assert os.path.exists(result)
    assert os.path.exists(subfolder)


def test_copy_dry():

  # Tests if can organize at least the sample photo

  # Temporary setup
  src = data_path('img_with_exif.jpg')
  fmt = '%Y/%B/%d.%m.%Y'

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:
    subfolder = os.path.join(base, 'subfolder')
    os.mkdir(subfolder)
    shutil.copy2(src, subfolder)
    src = os.path.join(subfolder, os.path.basename(src))
    result = copy(src, dst, fmt, timestamp=False, nodate='nodate', move=False,
        dry=True)
    assert os.path.exists(subfolder)
    assert not os.path.exists(result)


def test_move_many():

  # Tests if we can move a whole ensemble of files

  data = data_path()
  fmt = '%Y/%B/%d.%m.%Y'

  # Ground truth
  bad_src = ['unsupported.txt']
  bad_src = [os.path.join(os.path.basename(data), k) for k in bad_src]
  good_src = [
      'img_with_exif.jpg',
      'img_without_exif.jpg',
      'img_with_xmp.png',
      'img_without_xmp.png',
      'mp4.mp4',
      'mp4.mp4',
      'editing_info.aae',
      'img.heic',
      ]
  good_src = [os.path.join(os.path.basename(data), k) for k in good_src]
  good_dst = [
      os.path.join('2003', 'december', '14.12.2003', 'img_with_exif.jpg'),
      os.path.join('nodate', 'img_without_exif.jpg'),
      os.path.join('2017', 'august', '29.08.2017', 'img_with_xmp.png'),
      os.path.join('nodate', 'img_without_xmp.png'),
      os.path.join('2005', 'october', '28.10.2005', 'mp4.mp4'),
      os.path.join('2002', 'january', '26.01.2002', 'editing_info.aae'),
      os.path.join('2002', 'january', '26.01.2002', 'img.heic'),
      ]

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:
    src = os.path.join(base, os.path.basename(data))
    shutil.copytree(data, src)
    good, bad = rcopy(base, dst, fmt, timestamp=False, nodate='nodate',
        move=True, dry=False)
    bad_full = [os.path.join(base, k) for k in bad_src]
    nose.tools.eq_(sorted(bad_full), sorted(bad))
    for k in bad_full:
      assert os.path.exists(k), '%r does not exist' % k
    good_full = [os.path.join(dst, k) for k in good_dst]
    nose.tools.eq_(sorted(good_full), sorted(good))
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
  bad_src = ['unsupported.txt']
  bad_src = [os.path.join(os.path.basename(data), k) for k in bad_src]
  good_src = [
      'img_with_exif.jpg',
      'img_without_exif.jpg',
      'img_with_xmp.png',
      'img_without_xmp.png',
      'mp4.mp4',
      'editing_info.aae',
      'img.heic',
      ]
  good_src = [os.path.join(os.path.basename(data), k) for k in good_src]
  good_dst = [
      os.path.join('2003', 'december', '14.12.2003', 'img_with_exif.jpg'),
      os.path.join('nodate', 'img_without_exif.jpg'),
      os.path.join('2017', 'august', '29.08.2017', 'img_with_xmp.png'),
      os.path.join('nodate', 'img_without_xmp.png'),
      os.path.join('2005', 'october', '28.10.2005', 'mp4.mp4'),
      os.path.join('2002', 'january', '26.01.2002', 'editing_info.aae'),
      os.path.join('2002', 'january', '26.01.2002', 'img.heic'),
      ]

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:
    src = os.path.join(base, os.path.basename(data))
    shutil.copytree(data, src)

    # remove unwanted files
    for k in bad_src:
      os.unlink(os.path.join(base, k))

    good, bad = rcopy(base, dst, fmt, timestamp=False, nodate='nodate',
        move=True, dry=False)

    assert len(bad) == 0

    good_full = [os.path.join(dst, k) for k in good_dst]
    nose.tools.eq_(sorted(good_full), sorted(good))
    for k in good_full:
      assert os.path.exists(k), '%r does not exist' % k
    old_good_full = [os.path.join(base, k) for k in good_src]
    for k in old_good_full:
      assert not os.path.exists(k), '%r still exists' % k

    # asserts the original directory is removed up to, but excluding, src
    assert os.path.exists(src), '%r does not exist' % src
    assert os.path.exists(base), '%r does not exist' % base


def test_watch():

  # Tests if we can move a whole ensemble of files and that the source
  # directory is correctly removed

  data = data_path()
  fmt = '%Y/%B/%d.%m.%Y'

  # Ground truth
  bad_src = ['unsupported.txt']
  bad_src = [os.path.join(os.path.basename(data), k) for k in bad_src]
  good_src = [
      'img_with_exif.jpg',
      'img_without_exif.jpg',
      'img_with_xmp.png',
      'img_without_xmp.png',
      'mp4.mp4',
      ]
  good_src = [os.path.join(os.path.basename(data), k) for k in good_src]
  good_dst = [
      os.path.join('2003', 'december', '14.12.2003', 'img_with_exif.jpg'),
      os.path.join('nodate', 'img_without_exif.jpg'),
      os.path.join('2017', 'august', '29.08.2017', 'img_with_xmp.png'),
      os.path.join('nodate', 'img_without_xmp.png'),
      os.path.join('2005', 'october', '28.10.2005', 'mp4.mp4'),
      ]

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:

    sorter = Sorter(base, dst, fmt, timestamp=False, nodate='nodate',
        move=True, dry=False, email=False, hostname='docker',
        sender='joe@example.com', to=['alice@example.com'],
        server='smtp.gmail.com', port=587, username='dummy@gmail.com',
        password='there-you-go', idleness=1)
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
  bad_src = ['unsupported.txt']
  bad_src = [os.path.join(os.path.basename(data), k) for k in bad_src]
  good_src = [
      'img_with_exif.jpg',
      'img_without_exif.jpg',
      'img_with_xmp.png',
      'img_without_xmp.png',
      'mp4.mp4',
      ]
  good_src = [os.path.join(os.path.basename(data), k) for k in good_src]
  good_dst = [
      os.path.join('2003', 'december', '14.12.2003', 'img_with_exif.jpg'),
      os.path.join('nodate', 'img_without_exif.jpg'),
      os.path.join('2017', 'august', '29.08.2017', 'img_with_xmp.png'),
      os.path.join('nodate', 'img_without_xmp.png'),
      os.path.join('2005', 'october', '28.10.2005', 'mp4.mp4'),
      ]

  with TemporaryDirectory() as start, TemporaryDirectory() as base, \
      TemporaryDirectory() as dst:

    sorter = Sorter(base, dst, fmt, timestamp=False, nodate='nodate',
        move=True, dry=False, email=False, hostname='docker',
        sender='joe@example.com', to=['alice@example.com'],
        server='smtp.gmail.com', port=587, username='dummy@gmail.com',
        password='there-you-go', idleness=1)
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
  bad_src = ['unsupported.txt']
  bad_src = [os.path.join(os.path.basename(data), k) for k in bad_src]
  good_src = [
      'img_with_exif.jpg',
      'img_without_exif.jpg',
      'img_with_xmp.png',
      'img_without_xmp.png',
      'mp4.mp4',
      ]
  good_src = [os.path.join(os.path.basename(data), k) for k in good_src]
  good_dst = [
      os.path.join('2003', 'december', '14.12.2003', 'img_with_exif.jpg'),
      os.path.join('nodate', 'img_without_exif.jpg'),
      os.path.join('2017', 'august', '29.08.2017', 'img_with_xmp.png'),
      os.path.join('nodate', 'img_without_xmp.png'),
      os.path.join('2005', 'october', '28.10.2005', 'mp4.mp4'),
      ]

  with TemporaryDirectory() as base, TemporaryDirectory() as dst:

    # simulates moving data into the base directory before watchdog is started
    src = os.path.join(base, os.path.basename(data))
    shutil.copytree(data, src)

    # remove unwanted files
    for k in bad_src:
      os.unlink(os.path.join(base, k))

    sorter = Sorter(base, dst, fmt, timestamp=False, nodate='nodate',
        move=True, dry=False, email=False, hostname='docker',
        sender='joe@example.com', to=['alice@example.com'],
        server='smtp.gmail.com', port=587, username='dummy@gmail.com',
        password='there-you-go', idleness=1)
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
    assert not os.path.exists(src), '%r still exists' % src
    assert os.path.exists(base), '%r does not exist' % base
