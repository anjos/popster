#!/usr/bin/env bash

# This script is used internally by conda-build-docker.sh to run all that is
# necessary to build a package using the conda-concourse-ci image.
/work/scripts/prepare-docker.sh
/opt/miniconda/bin/conda build "$@"
