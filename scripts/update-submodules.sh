#!/bin/bash

if ! command -v git &>/dev/null; then
  echo "git is not installed."
  exit 1
fi

echo "Pulling changes"
echo ""

git pull --recurse-submodules
if [ $? -ne 0 ]; then
  echo "Failed to pull submodules"
  exit 1
fi

echo "Updating submodules recursively"
git submodule update --init --recursive --remote
if [ $? -ne 0 ]; then
  echo "Failed to update submodules"
  exit 1
fi

echo "Updated submodules"
exit 0
