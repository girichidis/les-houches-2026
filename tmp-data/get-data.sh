#!/bin/bash

for f in scaled-density-Teq-cube.pkl
do
   if [ ! -e $f ]
   then
      echo "downloading: $f"
      echo wget datentaxi.de/13/les-houches-2026/$f -O $f
   else
      echo "file $f already there!"
   fi
done
