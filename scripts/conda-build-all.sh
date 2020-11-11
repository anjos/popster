#!/usr/bin/env bash

# Script to build all conda packages on the current system
script_dir="$( cd "$(dirname "$0")" ; pwd -P )"

simple_pkgs=()
simple_pkgs+=('deps/mediainfo')

python_versions=()
python_versions+=('3.8')

python_pkgs=()
python_pkgs+=('deps/pymediainfo')
python_pkgs+=('conda') #popster itself

noarch_pkgs=()
noarch_pkgs+=('deps/exifread')

echo -e "#!/usr/bin/env bash\n"

for p in "${simple_pkgs[@]}"; do
  echo "## To build '${p}', issue the following:"
  echo conda build -c anjos --variant-config-files deps/conda_build_config.yaml ${p}
  echo ${script_dir}/conda-build-docker.sh /work/$p
  echo ""
done

for pyver in "${python_versions[@]}"; do
  for p in "${python_pkgs[@]}"; do
    echo "## To build '${p}', issue the following:"
    echo conda build -c anjos --python=$pyver --variant-config-files deps/conda_build_config.yaml $p
    echo ${script_dir}/conda-build-docker.sh --python=$pyver /work/$p
    echo ""
  done
done

for p in "${noarch_pkgs[@]}"; do
  echo "## To build '${p}', issue the following:"
  echo conda build -c anjos --variant-config-files deps/conda_build_config.yaml $p
  echo ""
done
