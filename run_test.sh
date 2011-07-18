#!/bin/bash

# rm logs/{color_,}core.log
# ./core.py && utilities/pylog.py logs/core.log logs/color_core.log && cat logs/color_core.log

if [ -e logs/core.log ]; then
  rm logs/core.log
fi
./core.py && utilities/pylog logs/core.log
