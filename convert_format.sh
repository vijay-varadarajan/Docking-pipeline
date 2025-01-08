#!/bin/bash

# Path to the OpenBabel container
OPENBABEL_CONTAINER="openbabel.sif"

# Read the CSV file
csv_file="csv/pairs.csv"
mapfile -t csv_lines < <(tail -n +2 "$csv_file" | sed 's/[[:space:]]*$//')

# Loop through the CSV lines
for i in "${!csv_lines[@]}"; do
    # Parse CSV row and trim whitespace
    IFS=',' read -r ligand_file receptor_file autobox_file <<< "$(echo "${csv_lines[$i]}" | sed 's/[[:space:]]*$//g' | sed 's/^[[:space:]]*//g')"

    # Check if the ligand file column is present
    if [ -z "$ligand_file" ]; then
        echo "Error: Missing ligand file in CSV file at line $((i+2))"
        continue
    fi

    # Append directory to the ligand and autobox file paths
    ligand_file="ligands/$ligand_file"
    autobox_file="sites/$autobox_file"

    # Check if input files exist
    if [ ! -f "$ligand_file" ]; then
        echo "Error: Ligand file $ligand_file not found."
        continue
    fi

    if [ ! -f "$autobox_file" ]; then
        echo "Error: Autobox file $autobox_file not found."
        continue
    fi

    # Generate output filenames by replacing extensions
    ligand_file_sdf="${ligand_file%.*}.sdf"
    autobox_file_sdf="${autobox_file%.*}.sdf"

    # Check and convert ligand file
    if [ -f "$ligand_file_sdf" ]; then
        echo "Output file $ligand_file_sdf already exists. Skipping conversion."
    else
        echo "Converting $ligand_file to SDF format..."
        obabel "$ligand_file" -O "$ligand_file_sdf"

        # Check the exit status of the command
        if [ $? -ne 0 ]; then
            echo "Error occurred during conversion of $ligand_file"
            continue
        else
            echo "Conversion of $ligand_file completed successfully"
        fi
    fi

    # Check and convert autobox file
    if [ -f "$autobox_file_sdf" ]; then
        echo "Output file $autobox_file_sdf already exists. Skipping conversion."
    else
        echo "Converting $autobox_file to SDF format..."
        obabel "$autobox_file" -O "$autobox_file_sdf"

        # Check the exit status of the command
        if [ $? -ne 0 ]; then
            echo "Error occurred during conversion of $autobox_file"
        else
            echo "Conversion of $autobox_file completed successfully"
        fi
    fi
done
