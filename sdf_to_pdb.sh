#!/bin/bash

# Directory containing the files
base_dir="output/"

# Loop through all .sdf files in the directory and subdirectories
find "$base_dir" -type f -name "*.sdf" | while read -r file; do
    # Generate the corresponding .pdb filename
    file_pdb="${file%.*}.pdb"
    
    # Convert the file to PDB format using OpenBabel
    echo "Converting $file to PDB format..."
    obabel "$file" -O "$file_pdb"
    
    # Check if the conversion was successful
    if [ $? -eq 0 ]; then
        echo "Conversion successful: $file_pdb"
        # Remove the original .sdf file
        rm "$file"
        echo "Removed original file: $file"
    else
        echo "Error during conversion of $file"
    fi
done
