FROM condaforge/mambaforge:latest

# Install conda
RUN CONDA_DIR="/opt/conda" && \
    $CONDA_DIR/bin/conda config --set auto_update_conda False && \
    $CONDA_DIR/bin/mamba install --name=base --channel=anjos popster=1.4.3 && \
    $CONDA_DIR/bin/conda clean --all --yes && \
    mkdir -p "$CONDA_DIR/locks" && \
    chmod 777 "$CONDA_DIR/locks"

# Export this command
ENV PATH="/opt/conda/bin:${PATH}"
ENTRYPOINT ["/opt/conda/bin/watch"]
CMD ["--help"]
