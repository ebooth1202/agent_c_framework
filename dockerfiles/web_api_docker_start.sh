#!/bin/bash
set -e

# Go to the directory containing this script
cd "$(dirname "$0")"

# Build and start the containers, uncomment to run in attached mode:
#docker-compose up --build

# To run in detached mode (background), uncomment to run in detached mode:
 docker-compose up --build -d