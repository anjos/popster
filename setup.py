#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from setuptools import setup, find_packages

setup(
    name="popster",
    version="1.4.1",
    description="A pythonic photo importer for my QNAP NAS",
    url="https://github.com/anjos/popster",
    license="GPLv3",
    author="Andre Anjos",
    author_email="andre.dos.anjos@gmail.com",
    long_description=open("README.rst").read(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "docopt",
        "watchdog",
        "exifread",
        "pymediainfo",
        "pillow",
        "tqdm",
    ],
    entry_points={
        "console_scripts": [
            "watch = popster.watch:main",
            "check_date = popster.check_date:main",
            "heic_to_jpeg = popster.heic_to_jpeg:main",
            "deduplicate = popster.deduplicate:main",
            "logs = popster.logs:main",
            "deploy = popster.deploy:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
)
