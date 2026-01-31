#!/bin/bash

# Navigate to the project directory
# Modify this path if you clone the repo somewhere else
cd ~/rice-quality-system

echo "Starting Deployment..."

# Force fresh pull
echo "Fetching latest changes..."
git fetch --all
git reset --hard origin/main
git clean -fd

# Rebuild and restart the containers
echo "Rebuilding and restarting containers..."
# --build forces a rebuild of the images to include latest code changes
# -d runs containers in the background
sudo docker-compose up -d --build

# Prune unused docker objects to save space (optional but good for small instances)
echo "Cleaning up..."
sudo docker image prune -f

echo "Deployment completed successfully!"
