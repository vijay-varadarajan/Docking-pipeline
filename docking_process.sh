#!/bin/bash

# blind - Boolean, if true, the ligand is docked blindly, without using any information about the binding site. If you pass false - Sitespecific Docking.
# scoring - If vinardo/Vina, pass cnn_scoring none, and then provide values. 


while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --mode) mode="$2"; shift; shift ;;
    --scoring) scoring="$2"; shift; shift ;;
    --cnn_scoring) cnn_scoring="$2"; shift; shift ;;
    --exhaustiveness) exhaustiveness="$2"; shift; shift;;
    --num_modes) num_modes="$2"; shift; shift;;
    --blind) blind="$2"; shift; shift;;
    --input_file) input_file="$2"; shift; shift;;
    --PREVIOUS_RELEASE_TIMESTAMP) PREVIOUS_RELEASE_TIMESTAMP="$2"; shift; shift;;
    *)
      echo "Unknown option: $key"
      exit 1
      ;;
  esac
done


gnina_docking() {
    
    mkdir -p output
    rm -rf output/*

    mapfile -t csv_lines < <(tail -n +2 "$input_file")
    for i in "${!csv_lines[@]}"; do
        IFS=',' read -r receptor_file ligand_file autobox_file center_x center_y center_z size_x size_y size_z <<< "${csv_lines[$i]}"
        if [ -z "$ligand_file" ] || [ -z "$receptor_file" ] || [ -z "$autobox_file" ]; then
            echo "Error: Missing columns in CSV file at line $((i+2))"
            continue
        fi
        
        ligand_file="ligands/${ligand_file}"
        receptor_file="proteins/$receptor_file"
        autobox_file="sites/${autobox_file}"

        # basename of ligandfile without sdf extension
        receptor_file_basename="$(basename "$receptor_file" .sdf)"
        ligand_file_basename="$(basename "$ligand_file" .sdf)"
        autobox_file_basename="$(basename "$autobox_file" .sdf)"

        output_file="output/$(basename "$receptor_file_basename" .pdb)_$(basename "$ligand_file_basename" .pdb).sdf.gz"

        # Start building the base command
        gnina_cmd="gnina -r $receptor_file -l $ligand_file"

        # # If Blind docking is true
        if [ "$blind" -ne 0 ]; then
            gnina_cmd+=" --autobox_ligand $receptor_file"
        else
            if [ -n "$autobox_file" ]; then
                autobox_file="${autobox_file%.*}.pdb"
                gnina_cmd+=" --autobox_ligand $autobox_file"
            elif [ -n "$center_x" ] && [ -n "$center_y" ] && [ -n "$center_z" ] && 
                 [ -n "$size_x" ] && [ -n "$size_y" ] && [ -n "$size_z" ]; then
                gnina_cmd+=" --center_x $center_x --center_y $center_y --center_z $center_z"
                gnina_cmd+=" --size_x $size_x --size_y $size_y --size_z $size_z"
            else
                echo "Error: Missing site or grid dimensions in CSV file at line $((i+2))"
                continue
            fi
        fi

        # # Add optional flags
        [ -n "$exhaustiveness" ] && gnina_cmd+=" --exhaustiveness $exhaustiveness"
        [ -n "$scoring" ] && gnina_cmd+=" --scoring $scoring"
        [ -n "$cnn_scoring" ] && gnina_cmd+=" --cnn_scoring $cnn_scoring"
        [ -n "$num_modes" ] && gnina_cmd+=" --num_modes $num_modes"

        # # Add the output file flag
        gnina_cmd+=" -o $output_file"
        $gnina_cmd
        echo "Executing docking for line number $((i+1)) in csv file..."
    done
}


plip_processing() {
    if [ "$#" -ne 0 ]; then
        echo "Usage: $0 plip"
        exit 1
    fi

    for folder in output/*/; do
        for pdb_file in "$folder"docked_*.pdb; do
            if [ -f "$pdb_file" ]; then
                plip -f "$pdb_file" -x
                
                base_name=$(basename "$pdb_file" .pdb)
                mv report.xml "$folder"report_${base_name}.xml

                rm ./*.pdb
            fi
        done
    done
}


unzip_files() {
    if [ "$#" -ne 0 ]; then
        echo "Usage: $0 unzip"
        exit 1
    fi

    for file in output/*.gz; do
        if [ -f "$file" ]; then
            echo "Unzipping $file..."
            gunzip "$file"
            
            if [ $? -ne 0 ]; then
                echo "Error occurred during unzipping of $file"
            else
                echo "Unzipping of $file completed successfully"
            fi
        else
            echo "No .gz files found in the output folder."
            break
        fi
    done
}


sdf_to_pdb() {    
    if [ "$#" -ne 0 ]; then
        echo "Usage: $0 sdftopdb"
        exit 1
    fi

    base_dir="output/"

    find "$base_dir" -type f -name "*.sdf" | while read -r file; do
        file_pdb="${file%.*}.pdb"
        
        echo "Converting $file to PDB format..."
        obabel "$file" -O "$file_pdb"
        
        if [ $? -eq 0 ]; then
            echo "Conversion successful: $file_pdb"
            rm "$file"
            echo "Removed original file: $file"
        else
            echo "Error during conversion of $file"
        fi
    done
}


case "$mode" in
    gnina)
        gnina_docking "$@"
        ;;
    plip)
        plip_processing "$@"
        ;;
    sdftopdb)
        sdf_to_pdb "$@"
        ;;
    unzip)
        unzip_files "$@"
        ;;
    *)
        echo "Invalid command: $command"
        echo "Usage: $0 {convert|gnina|plip|sdftopdb|unzip} [args...]"
        exit 1
        ;;
esac
