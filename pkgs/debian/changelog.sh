#!/bin/bash

DISTR_NAME=$(lsb_release -is|sed s/' '//g) 
DISTR_REL=$(lsb_release -rs|sed s/' '//g)

nam="raster-tools"
build=3
mant="Baev Aleksandr <old_bay@mail.ru>"
ver=$(cat setup.py |grep version|awk -F "=" '{print $2}'|awk -F "'" '{print $2}')

echo "${nam} (${ver}-${build}+${DISTR_NAME}${DISTR_REL}) unstable; urgency=low"
cat <<\EOF

  * Update

EOF
echo " -- ${mant}  $(date -R)"
