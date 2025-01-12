#!/bin/bash

convert_format() {
    if [ "$#" -ne 1 ]; then
        echo "Usage: $0 convert <csv_file>"
        exit 1
    fi
    
    csv_file=$1
    
    # Check if CSV file exists
    if [ ! -f "$csv_file" ]; then
        echo "Error: CSV file $csv_file not found"
        exit 1
    fi

    mapfile -t csv_lines < <(tail -n +2 "$csv_file" | sed 's/[[:space:]]*$//')

    # Rest of the convert_format function remains the same
    for i in "${!csv_lines[@]}"; do
        IFS=',' read -r ligand_file receptor_file autobox_file <<< "$(echo "${csv_lines[$i]}" | sed 's/[[:space:]]*$//g' | sed 's/^[[:space:]]*//g')"

        if [ -z "$ligand_file" ]; then
            echo "Error: Missing ligand file in CSV file at line $((i+2))"
            continue
        fi

        ligand_file="ligands/$ligand_file"
        autobox_file="sites/$autobox_file"

        if [ ! -f "$ligand_file" ]; then
            echo "Error: Ligand file $ligand_file not found."
            continue
        fi

        if [ ! -f "$autobox_file" ]; then
            echo "Error: Autobox file $autobox_file not found."
            continue
        fi

        ligand_file_sdf="${ligand_file%.*}.sdf"
        autobox_file_sdf="${autobox_file%.*}.sdf"

        if [ -f "$ligand_file_sdf" ]; then
            echo "Output file $ligand_file_sdf already exists. Skipping conversion."
        else
            echo "Converting $ligand_file to SDF format..."
            obabel "$ligand_file" -O "$ligand_file_sdf"
            if [ $? -ne 0 ]; then
                echo "Error occurred during conversion of $ligand_file"
                continue
            else
                echo "Conversion of $ligand_file completed successfully"
            fi
        fi

        if [ -f "$autobox_file_sdf" ]; then
            echo "Output file $autobox_file_sdf already exists. Skipping conversion."
        else
            echo "Converting $autobox_file to SDF format..."
            obabel "$autobox_file" -O "$autobox_file_sdf"
            if [ $? -ne 0 ]; then
                echo "Error occurred during conversion of $autobox_file"
            else
                echo "Conversion of $autobox_file completed successfully"
            fi
        fi
    done
}

gnina_docking() {
    if [ "$#" -ne 2 ]; then
        echo "Usage: $0 gnina <cnn_scoring> <csv_file>"
        exit 1
    fi

    cnn_scoring=$1
    csv_file=$2

    # Check if CSV file exists
    if [ ! -f "$csv_file" ]; then
        echo "Error: CSV file $csv_file not found"
        exit 1
    fi

    mapfile -t csv_lines < <(tail -n +2 "$csv_file")

    for i in "${!csv_lines[@]}"; do
        IFS=',' read -r ligand_file receptor_file autobox_file <<< "${csv_lines[$i]}"
        
        if [ -z "$ligand_file" ] || [ -z "$receptor_file" ] || [ -z "$autobox_file" ]; then
            echo "Error: Missing columns in CSV file at line $((i+2))"
            continue
        fi
        
        ligand_file=ligands/${ligand_file%.*}.sdf
        receptor_file=proteins/$receptor_file
        autobox_file=sites/${autobox_file%.*}.sdf

        mkdir -p output
        output_file="output/$(basename $ligand_file .sdf)_$(basename $receptor_file .pdb)_$(basename $autobox_file .sdf).sdf.gz"
        
        echo "Executing iteration $((i+1))..."
        
        gnina -l $ligand_file -r $receptor_file --autobox_ligand $autobox_file -o $output_file --cnn_scoring $cnn_scoring
        
        if [ $? -ne 0 ]; then
            echo "Error occurred during iteration $((i+1))"
        else
            echo "Iteration $((i+1)) completed successfully"
        fi
    done
}

plip_processing() {
    if [ "$#" -ne 0 ]; then
        echo "Usage: $0 plip"
        exit 1
    fi

    for folder in output/*/; do
        for pdb_file in "$folder"combined_*.pdb; do
            if [ -f "$pdb_file" ]; then
                plip -f "$pdb_file" -x
                
                base_name=$(basename "$pdb_file" .pdb)
                mv report.xml "$folder"report_${base_name}.xml

                rm ./*.pdb
            fi
        done
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

# Main script logic
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 {convert|gnina|plip|sdftopdb|unzip} [args...]"
    echo
    echo "Commands:"
    echo "  convert <csv_file>           Convert files according to CSV specification"
    echo "  gnina <cnn_scoring> <csv_file>   Run gnina docking"
    echo "  plip                         Process files with PLIP"
    echo "  sdftopdb                     Convert SDF files to PDB format"
    echo "  unzip                        Unzip .gz files in output directory"
    exit 1
fi

command=$1
shift

case "$command" in
    convert)
        convert_format "$@"
        ;;
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