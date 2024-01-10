import ROOT
import sys
import os

v4_start = 367765

# Get a path with the root files in the directory and its subdirectories from the command line
if len(sys.argv) < 2:
    print("Please provide a path to the root files")
    sys.exit(1)
path = sys.argv[1]

# Get the root files
root_files = []
for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith(".root"):
            root_files.append(os.path.join(root, file))
            
# Go through the root files, find the max and min run numbers
mixed = 0
before = 0
after = 0
for file in root_files:
    print(f"Processing {file}")
    rdf = ROOT.RDataFrame("Events", file)
    run_max = rdf.Max("run").GetValue()
    run_min = rdf.Min("run").GetValue()
    
    if (run_min < v4_start) and (run_max < v4_start):
        print("Before v4")
        before += 1
    elif (run_min < v4_start) and (run_max >= v4_start):
        print("Mixed")
        mixed += 1
    elif (run_min >= v4_start) and (run_max >= v4_start):
        print("After v4")
        after += 1

print(f"Before v4: {before}")
print(f"Mixed: {mixed}")
print(f"After v4: {after}")