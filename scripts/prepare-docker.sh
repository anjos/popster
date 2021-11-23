#!/usr/bin/env bash

# Prepares the docker container for a build
conda_dir="/opt/conda"
condarc="${conda_dir}/condarc"

rm -f ~/.condarc

cat <<EOF > ${condarc}
default_channels: #!final
  - https://repo.continuum.io/pkgs/main
add_pip_as_python_dependency: false #!final
changeps1: false #!final
always_yes: true #!final
quiet: true #!final
show_channel_urls: true #!final
channel_priority: strict #!final
anaconda_upload: false #!final
ssl_verify: false #!final
channels: #!final
EOF

echo "  - conda-forge" >> ${condarc}

# displays contents of our configuration
echo "Contents of \`${condarc}':"
cat ${condarc}

# updates conda installation
${conda_dir}/bin/conda install -n base conda-build

# print conda information for debugging purposes
${conda_dir}/bin/conda info
