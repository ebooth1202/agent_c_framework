#!/bin/bash
set -e

# Go to the directory containing this script
cd "$(dirname "$0")"

# To run in detached mode (background), uncomment to run in detached mode:
 docker-compose -f docker-compose.yml -p agent_c up --build -d