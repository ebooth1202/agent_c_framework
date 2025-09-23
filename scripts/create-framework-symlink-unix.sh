#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Calculate the project root (one directory up from scripts folder)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Get the project folder name for default link name
DEFAULT_LINK_NAME="$(basename "$PROJECT_ROOT")"

# Use provided name or default to project folder name
LINK_NAME="${1:-$DEFAULT_LINK_NAME}"

# Define desktop path
DESKTOP_PATH="$HOME/Desktop"

echo "Project location detected as: $PROJECT_ROOT"
echo ""

# Create the symbolic link
echo "Creating symbolic link on desktop as: $LINK_NAME"

# Check if a folder or link with that name already exists
if [ -e "$DESKTOP_PATH/$LINK_NAME" ]; then
    echo "Warning: A folder or link named '$LINK_NAME' already exists on the desktop."
    read -p "Do you want to replace it? (y/n): " OVERWRITE
    if [[ "$OVERWRITE" =~ ^[Yy]$ ]]; then
        rm -rf "$DESKTOP_PATH/$LINK_NAME"
    else
        echo "Operation cancelled by user."
        exit 0
    fi
fi

# Create the symbolic link
ln -s "$PROJECT_ROOT" "$DESKTOP_PATH/$LINK_NAME"

if [ $? -eq 0 ]; then
    echo ""
    echo "Success! Symbolic link created on desktop."
    echo "Link: $DESKTOP_PATH/$LINK_NAME"
    echo "Target: $PROJECT_ROOT"
else
    echo ""
    echo "Error: Failed to create symbolic link."
    echo "Please make sure you have the necessary permissions."
fi
