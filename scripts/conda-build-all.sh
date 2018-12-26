#!/usr/bin/env bash

# Script to build all conda packages on the current system
script_dir="$( cd "$(dirname "$0")" ; pwd -P )"

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
  conda build --variant-config-files deps/conda_build_config.yaml ${p}
  ${script_dir}/conda-build-docker.sh /work/$p
done

for pyver in "${python_versions[@]}"; do
  for p in "${python_pkgs[@]}"; do
    conda build --python=$pyver --variant-config-files deps/conda_build_config.yaml $p
    ${script_dir}/conda-build-docker.sh --python=$pyver /work/$p
  done
done
