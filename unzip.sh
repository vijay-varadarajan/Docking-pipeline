#!/bin/bash

# Unzip all .gz files in the output folder
for file in output/*.gz; do
    if [ -f "$file" ]; then
        echo "Unzipping $file..."
        gunzip "$file"
        
        # Check the exit status of the command
        if [ $? -ne 0 ]; then
            echo "Error occurred during unzipping of $file"
        else
            echo "Unzipping of $file completed successfully"
        fi
    else
        echo "No .gz files found in the output folder."
    fi
done
