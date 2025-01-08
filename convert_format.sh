#!/bin/bash

# Path to the OpenBabel container
OPENBABEL_CONTAINER="openbabel.sif"

# Read the CSV file
csv_file="csv/pairs.csv"
mapfile -t csv_lines < <(tail -n +2 "$csv_file")

# Loop through the CSV lines
for i in "${!csv_lines[@]}"; do
    IFS=',' read -r ligand_file receptor_file autobox_file <<< "${csv_lines[$i]}"

    # Check if the ligand file column is present
    if [ -z "$ligand_file" ]; then
        echo "Error: Missing ligand file in CSV file at line $((i+2))"
        continue
    fi

    # Append directory to the ligand and autobox file paths
    ligand_file="ligands/$ligand_file"
    autobox_file="sites/$autobox_file"

    # Generate output filenames by replacing extensions
    ligand_file_sdf="${ligand_file%.*}.sdf"
    autobox_file_sdf="${autobox_file%.*}.sdf"

    # Convert files using OpenBabel
    echo "Converting $ligand_file to PDB format..."
    obabel "$ligand_file" -O "$ligand_file_sdf"

    echo "Converting $autobox_file to PDB format..."
    obabel "$autobox_file" -O "$autobox_file_sdf"

    # Check the exit status of the commands
    if [ $? -ne 0 ]; then
        echo "Error occurred during conversion of $ligand_file or $autobox_file"
    else
        echo "Conversion of $ligand_file and $autobox_file completed successfully"
    fi
done
