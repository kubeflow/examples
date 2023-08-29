#!/usr/bin/env bash

target=$1

if [ "$#" -eq 1 ]
then
    USERDIR=/data/$target
else
    USERDIR=/data/0.helloworld
fi

echo "run with userdir=$USERDIR"

USERDIR=$USERDIR docker compose up
#USERDIR=$USERDIR docker compose convert
