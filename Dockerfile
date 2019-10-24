FROM frolvlad/alpine-glibc:alpine-3.7

# Install conda
RUN CONDA_DIR="/opt/conda" && \
    CONDA_VERSION="4.7.12" && \
    CONDA_MD5_CHECKSUM="0dba759b8ecfc8948f626fa18785e3d8" && \
    \
    apk add --no-cache --virtual=.build-dependencies wget ca-certificates bash && \
    \
    mkdir -p "$CONDA_DIR" && \
    wget "http://repo.continuum.io/miniconda/Miniconda3-${CONDA_VERSION}-Linux-x86_64.sh" -O miniconda.sh && \
    echo "$CONDA_MD5_CHECKSUM  miniconda.sh" | md5sum -c && \
    bash miniconda.sh -f -b -p "$CONDA_DIR" && \
    echo "export PATH=$CONDA_DIR/bin:\$PATH" > /etc/profile.d/conda.sh && \
    rm miniconda.sh && \
    \
    $CONDA_DIR/bin/conda update --yes conda && \
    $CONDA_DIR/bin/conda config --set auto_update_conda False && \
    $CONDA_DIR/bin/conda install --name=base --channel=anjos popster=1.4.0 && \
    rm -r "$CONDA_DIR/pkgs/" && \
    \
    apk del --purge .build-dependencies && \
    \
    mkdir -p "$CONDA_DIR/locks" && \
    chmod 777 "$CONDA_DIR/locks"

# Export this command
ENTRYPOINT ["/opt/conda/bin/watch"]
CMD ["--help"]
