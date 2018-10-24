#!/bin/bash

thisdir=$(dirname $0)
libdir=$(readlink -f ${thisdir}/..)

export PYTHONPATH="$libdir:$PYTHONPATH"
echo $PYTHONPATH
