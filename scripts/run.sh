#!/bin/bash

# Check if directory path is provided
if [ -z "$1" ]; then
  echo "Please provide a directory path."
  return
fi

# Iterate over subdirectories, ignoring PromptReco-v4
find "$1" -mindepth 2 -type d -not -path '*PromptReco-v4*' | while read -r dir; do
  # Get all .root files in subdirectory
  files=$(find "$dir" -type f -name "*.root")
  
  # If there are no .root files, continue to the next iteration
  if [ -z "$files" ]; then
    continue
  fi

  # Get the name of the subdirectory
  subdir_name=$(basename "$dir")

  # Determine the IOV based on the subdirectory name
  if [[ "$subdir_name" == *"Run2023B"* ]]; then
    iov="2023B"
  elif [[ "$subdir_name" == *"Run2023C"* && ("$subdir_name" == *"_v1-"* || "$subdir_name" == *"_v2-"* || "$subdir_name" == *"_v3-"*) ]]; then
    iov="2023Cv123"
  elif [[ "$subdir_name" == *"Run2023D"* ]]; then
    iov="2023D"
  else
    iov=""
  fi

  # Print the current subdirectory
  echo "Running on subdirectory: $subdir_name with IOV: $iov"

  # Run tauFilter.py for each subdirectory in the background
  python3 tauFilter.py --inputFiles $files --outputFile "../${subdir_name}_taus" --IOV $iov &
done

# Wait for all background jobs to finish
wait