#!/bin/bash

#for f in SILCC_hdf5_plt_cnt_3000-uniform-cube-N512.pkl SILCC_hdf5_plt_cnt_3000-uniform-cube-N256-full.pkl SILCC_hdf5_plt_cnt_3000
for f in SILCC_hdf5_plt_cnt_3000-uniform-cube-N512.pkl SILCC_hdf5_plt_cnt_3000-uniform-cube-N256-full.pkl
do
   if [ ! -e $f ]
   then
      echo "downloading: $f"
      echo wget datentaxi.de/13/les-houches-2026/$f -O $f
   else
      echo "file $f already there!"
   fi
done
