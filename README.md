# Docking Automation Pipeline

## Introduction

This project automates the process of docking ligands to proteins using various docking methods and scoring techniques provided by GNINA. It reads input data from a CSV file, converts necessary files, performs docking, and filters the results based on specified criteria.

## Usage

To run the docking automation script, use the following command:

```bash
python main.py --csv_path <csv_path> --cnn_scoring <scoring_type> --filter_type <filter_type>
```

### Command Line Arguments

- `--csv_path` (required): Path to the CSV file containing the protein, ligand, and site information.
- `--cnn_scoring` (required): CNN scoring method. Choices are `none`, `rescore`, `refinement`, `metrorescore`, `metrorefine`, `all`. Default is `rescore`.
- `--filter_type` (required): Filter type. Choices are `all` or `best`.


## Example

Here is an example command to run the script:

```bash
python main.py --csv_path ./csv/pairs.csv --cnn_scoring rescore --filter_type best
```


## Working

1. **CSV Parsing**: The script reads the protein, ligand, and site information from the specified CSV file.
2. **File Conversion**: Converts PDB files to SDF format using Open Babel.
3. **Docking**: Performs docking using the specified CNN scoring method.
4. **Filtering**: Filters the docked results based on the specified filter type.


## File Descriptions

### main.py

The main script that orchestrates the entire process. It reads input data, converts files, performs docking, and filters results.

### pdb_to_sdf.py

Contains the function to convert PDB files to SDF format using Open Babel.

### docking.py

Contains functions to perform traditional docking, CNN scoring docking, and whole protein docking.

### filter_docked.py

Contains functions to filter the docked results based on the specified criteria.


## Dependencies

- Python 3.x
- RDKit
- OpenBabel
- Singularity
- Gnina


## SETUP 

### Singularity installation

Run the shell script located in the link below
https://github.com/Mys7erio/scientiflow-singularity/blob/main/install-singularity.sh

### Python and OpenBabel containers installation using Singularity

`singularity pull python.sif library://scientiflow/bioinformatics/python:3.12`

`singularity pull openbabel.sif library://scientiflow/bioinformatics/openbabel:3.1.0`

`singularity pull gnina.sif docker://gnina/gnina:latest`


## License

This project is licensed under the MIT License.
