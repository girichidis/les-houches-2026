#!/bin/bash

for f in SILCC_hdf5_plt_cnt_3000-uniform-cube-512.pkl SILCC_hdf5_plt_cnt_3000
do
   if [ ! -e ]
   then
      echo "downloading: $f"
      wegt blu4:www/13/les-houches-2026/$f -O $f
   else
      echo "file $f already there!"
   fi
done
