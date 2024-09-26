#!/bin/bash


set -e  # Exit immediately if a command exits with a non-zero status.

# Directory containing the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Subdirectory to update
SUBDIR="install_module"

# Full path to the subdirectory
SUBDIR_PATH="$SCRIPT_DIR/$SUBDIR"

# GitHub repository URL
REPO_URL="https://github.com/seapoe1809/Health_server"

# Update the install_module subdirectory
if [ -d "$SUBDIR_PATH/.git" ]; then
    echo "Updating existing $SUBDIR directory..."
    cd "$SUBDIR_PATH"
    git fetch origin
    
    # Check if 'main' branch exists
    if git ls-remote --exit-code --heads origin main >/dev/null 2>&1; then
        BRANCH="main"
    elif git ls-remote --exit-code --heads origin master >/dev/null 2>&1; then
        BRANCH="master"
    else
        echo "Error: Neither 'main' nor 'master' branch found in the remote repository."
        exit 1
    fi
    
    echo "Using branch: $BRANCH"
    git checkout $BRANCH
    git reset --hard origin/$BRANCH
else
    echo "Cloning $SUBDIR directory..."
    git clone "$REPO_URL" "$SUBDIR_PATH"
    cd "$SUBDIR_PATH"
    
    # Check which branch was cloned
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo "Cloned branch: $BRANCH"
fi

echo "Update complete."
