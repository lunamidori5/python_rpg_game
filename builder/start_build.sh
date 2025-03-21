#!/bin/bash

mkdir temp_game
mkdir output
mkdir output/windows
mkdir output/linux

cp -r -t temp_game/. ../*

# Build the Docker image
docker build --no-cache -t game-builder .

# Run the Docker container and wait until it finishes
docker run --rm -v $(pwd):/game -v $(pwd)/temp_game:/game-code game-builder

# Remove the Docker image
docker image rm game-builder

#butler push output/windows lunamidori/midori-endless-auto-fighter:windows
#butler push output/linux lunamidori/midori-endless-auto-fighter:linux

sleep 600

rm -rf output
rm -rf temp_game