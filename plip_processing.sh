for folder in output/*/; do
    # Find the combined_*.pdb file in the current folder
    for pdb_file in "$folder"combined_*.pdb; do
        if [ -f "$pdb_file" ]; then
            # Execute the plip command with the found pdb file
            singularity exec plip.sif plip -f "$pdb_file" -x
            
            # Rename the generated report.xml to report_filename.xml
            base_name=$(basename "$pdb_file" .pdb)
            mv report.xml "$folder"report_${base_name}.xml

            # remove other pdb files from the base folder
            rm ./*.pdb
        fi
    done
done