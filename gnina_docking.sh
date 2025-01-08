#!/bin/bash

# Path to the gnina container
GNINA_CONTAINER="gnina.sif"

# Accept command line argument for cnn_scoring
cnn_scoring=$1

# Read the CSV file
csv_file="csv/pairs.csv"
mapfile -t csv_lines < <(tail -n +2 "$csv_file")

# Loop through the CSV lines
for i in "${!csv_lines[@]}"; do
    IFS=',' read -r ligand_file receptor_file autobox_file <<< "${csv_lines[$i]}"
    
    # Check if all columns are present
    if [ -z "$ligand_file" ] || [ -z "$receptor_file" ] || [ -z "$autobox_file" ]; then
        echo "Error: Missing columns in CSV file at line $((i+2))"
        continue
    fi
    
    # Append directories to the file paths
    ligand_file=ligands/${ligand_file%.*}.sdf
    receptor_file=proteins/$receptor_file
    autobox_file=sites/${autobox_file%.*}.sdf

    mkdir -p output
    output_file="output/$(basename $ligand_file .sdf)_$(basename $receptor_file .pdb)_$(basename $autobox_file .sdf).sdf.gz"
    
    echo "Executing iteration $((i+1))..."
    
    # Run the gnina command using Singularity

    gnina -l $ligand_file -r $receptor_file --autobox_ligand $autobox_file -o $output_file --cnn_scoring $cnn_scoring

    echo "gnina -l $ligand_file -r $receptor_file --autobox_ligand $autobox_file -o $output_file --cnn_scoring $cnn_scoring"
    
    # Check the exit status of the command
    if [ $? -ne 0 ]; then
        echo "Error occurred during iteration $((i+1))"
    else
        echo "Iteration $((i+1)) completed successfully"
    fi
done
