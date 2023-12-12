#!/bin/bash

# Check if directory path is provided
if [ -z "$1" ]; then
  echo "Please provide a directory path."
  exit 1
fi

# Iterate over subdirectories, ignoring PromptReco-v4
find "$1" -type d -not -path '*PromptReco-v4*' | while read -r dir; do
  # Get all .root files in subdirectory
  files=$(find "$dir" -type f -name "*.root")
  
  # If there are no .root files, continue to the next iteration
  if [ -z "$files" ]; then
    continue
  fi

  # Get the name of the subdirectory
  subdir_name=$(basename "$dir")

  # Print the current subdirectory
  echo "Running on subdirectory: $subdir_name"

  # Run tauFilter.py for each subdirectory in the background
  python3 tauFilter.py --inputFiles $files --outputFile "../${subdir_name}_taus" &
done

# Wait for all background jobs to finish
wait