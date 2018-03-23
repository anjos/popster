#!/usr/bin/env bash

# Prepares the docker container for a build
conda_dir="/opt/miniconda"
condarc="${conda_dir}/.condarc"

cat <<EOF > ${condarc}
default_channels: #!final
  - https://repo.continuum.io/pkgs/main
  - https://repo.continuum.io/pkgs/free
  - https://repo.continuum.io/pkgs/r
  - https://repo.continuum.io/pkgs/pro
add_pip_as_python_dependency: false #!final
changeps1: false #!final
always_yes: true #!final
quiet: true #!final
show_channel_urls: true #!final
anaconda_upload: false #!final
ssl_verify: false #!final
channels: #!final
EOF

echo "  - anjos" >> ${condarc}
echo "  - defaults" >> ${condarc}

# displays contents of our configuration
echo "Contents of \`${condarc}':"
cat ${condarc}

# updates conda installation
${conda_dir}/bin/conda install -n root conda conda-build

# cleans up
${conda_dir}/bin/conda clean --lock

# print conda information for debugging purposes
${conda_dir}/bin/conda info
