#!/usr/bin/env bash

# Runs conda-build-all.sh inside a properly setup docker container
# Examples:
# $0 /work/deps/mediainfo #builds which are pyton independent
# $0 --python=2.7 /work/deps/pymediainfo #builds which are python dependent

script_dir="$( cd "$(dirname "$0")" ; pwd -P )"
project_dir=$(dirname ${script_dir})
conda_dir=${HOME}/mamba
conda_bld=${conda_dir}/conda-bld
image="quay.io/condaforge/linux-anvil-cos7-x86_64:latest"

# Volumes to mount from the local work directory/conda build
volumes=()
volumes+=("${project_dir}:/work")
volumes+=("${conda_bld}:/opt/conda/conda-bld")

parameters="--tty"

for v in "${volumes[@]}"; do
  echo "[volume] $v"
  parameters="$parameters --volume $v";
done

# If you pass any parameters, we execute the build with the parameters of your
# choice, else, we assume you want to run interactively
if [ "$#" = "0" ]; then
  echo "Running interactively - execute /work/scripts/prepare-docker.sh"
  echo "  - only then you may run \`conda build <options> <recipe>'"
  docker run --rm ${parameters} --interactive ${image} bash
else
  echo "[${image}] automated - conda build $@"
  docker run --rm ${parameters} ${image} /work/scripts/run-on-docker.sh "$@"
fi
