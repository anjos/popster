#!/usr/bin/env bash

# Script to build all conda packages on the current system
conda_dir=$HOME/conda

simple_pkgs=()
#simple_pkgs+=('deps/mediainfo')

python_versions=()
python_versions+=('2.7')
python_versions+=('3.6')

python_pkgs=()
#python_pkgs+=('deps/pymediainfo')
#python_pkgs+=('deps/exifread')
#python_pkgs+=('deps/argh')
#python_pkgs+=('deps/pathtools')
#python_pkgs+=('deps/watchdog')
python_pkgs+=('conda') #popster itself

for p in "${simple_pkgs[@]}"; do
  conda build ${p}
done

for pyver in "${python_versions[@]}"; do
  for p in "${python_pkgs[@]}"; do
    conda build --python=$pyver $p
  done
done
