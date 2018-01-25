#! /bin/sh
if [ "${VIRTUALENV24}" ]; then
    VIRT24=${VIRTUALENV24}
else
    VIRT24='virtualenv'
fi

${VIRT24} -p python2.7 .
./bin/pip install --pypi-url=https://pypi.python.org/simple setuptools==33.1.1 zc.buildout==2.9.5
./bin/buildout "$@"
