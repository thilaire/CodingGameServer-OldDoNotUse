#! /bin/bash

#check for number of arguments
if [[ "$#" -ne 1 ]]; then
	echo "Usage: ./compile filename.c"
	exit
fi

# get given filename without extension
filename=`cut -d "." -f 1 <<< $1`

gcc -c -Wall $1 -I../API/
gcc -o $filename.out $filename.o ../API/starshipsAPI.o ../../../clientAPI/C/clientAPI.o
