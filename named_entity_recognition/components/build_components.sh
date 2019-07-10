#!/bin/bash

echo "\nBuild and push preprocess component"
sh ./preprocess/build_image.sh

echo "\nBuild and push train component"
sh ./train/build_image.sh

echo "\nBuild and push deploy component"
sh ./deploy/build_image.sh