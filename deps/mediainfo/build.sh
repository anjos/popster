#!/bin/bash

# Build script extracted from the file Compile_SO.sh at MediaInfo
# distribution. Modify according to changes in the original source

configure_options="--prefix=${PREFIX}"
if [ -n "${MACOSX_DEPLOYMENT_TARGET}" ]; then
  configure_options="${configure_options} --with-macosx-version-min=${MACOSX_DEPLOYMENT_TARGET}"
fi

pushd ZenLib/Project/GNU/Library/
test -e Makefile && rm -f Makefile
chmod +x configure
./configure ${configure_options} --enable-shared --disable-static
make -s -j${CPU_COUNT}
make install
popd

pushd MediaInfoLib/Project/GNU/Library/
test -e Makefile && rm Makefile
chmod +x configure
./configure ${configure_options} --enable-shared --disable-static --with-libcurl=${PREFIX}
make -s -j${CPU_COUNT}
make install
popd

pushd MediaInfo/Project/GNU/CLI/
test -e Makefile && rm Makefile
chmod +x configure
./configure ${configure_options}
make -s -j${CPU_COUNT}
make install
popd
