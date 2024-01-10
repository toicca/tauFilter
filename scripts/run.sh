#!/bin/bash

# Array to hold the PIDs of the background jobs
pids=()

# Check if directory path is provided
if [ -z "$1" ]; then
  echo "Please provide a directory path."
  return
fi

# Iterate over subdirectories, ignoring PromptReco-v4  19Dec2023
find "$1" -mindepth 1 -type d -not -path '*PromptReco-v4*' -not -path '*EGamma*' -not -path '*ZeroBias*' -not -path '*ReReco*' -path '*19Dec2023*' -path '*Run2022G*' | while read -r dir; do
# find "$1" -mindepth 1 -type d -not -path '*PromptReco-v4*' | while read -r dir; do
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
  elif [[ "$subdir_name" == *"Run2023C"* && ("$subdir_name" == *"_v4-"*)]]; then
    iov="2023Cv4"
  elif [[ "$subdir_name" == *"Run2023D"* ]]; then
    iov="2023D"
  elif [[ "$subdir_name" == *"Run2022B"* ]]; then
    iov="2022B"
  elif [[ "$subdir_name" == *"Run2022C"* ]]; then
    iov="2022C"
  elif [[ "$subdir_name" == *"Run2022D"* ]]; then
    iov="2022D"
  elif [[ "$subdir_name" == *"Run2022E"* ]]; then
    iov="2022E"
  elif [[ "$subdir_name" == *"Run2022F"* ]]; then
    iov="2022F"
  elif [[ "$subdir_name" == *"Run2022G"* ]]; then
    iov="2022G"
  else
    iov=""
  fi

  # Print the current subdirectory
  echo "Running on subdirectory: $subdir_name with IOV: $iov"

  # Run tauFilter.py for each subdirectory in the background
  python3 tauFilter.py --inputFiles $files --outputFile "../${subdir_name}_taus" --IOV $iov &

  # Save the PID of the background job
  pids+=($!)
done

# Wait for all background jobs to finish
for pid in ${pids[*]}; do
  wait $pid
done

# Change to upper directory
# cd ..

# Get a list of unique filenames after "JetMET0_" or "JetMET1_"
# filenames=$(ls JetMET* | cut -d'_' -f2- | sort | uniq)

# Loop over each unique filename
# for filename in $filenames
# do
  # Find all files with this filename after "JetMET0_" or "JetMET1_"
#   files=$(ls | grep "_${filename}$")

  # Use hadd to merge them
#   hadd "output/${filename}" $files

  # Change permissions of the merged file
#   chmod 777 "output/${filename}"
# done