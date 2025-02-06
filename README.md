# Docking Automation Pipeline

## Introduction

This project automates the process of docking ligands to proteins using various docking methods and scoring techniques provided by GNINA. It reads input data from a CSV file, converts necessary files, performs docking, and filters the results based on specified criteria, as explained below.

## Usage

Upload the input CSV file (`pairs.csv`) containing protein, ligand, and site information to the **csv/** directory. The CSV file should have the following columns:

- `protein`: Path to the protein PDB file.
- `ligand`: Path to the ligand PDB file.
- `site`: Path to the site PDB file.

Upload the required protein, ligand, and site PDB files to the **proteins/** , **ligands/** , and **sites/** directories, respectively.

To run the docking automation script, use the following command:

```bash
./main.sh
```

## Working

1. `singularity exec containers/openbabel-3.1.0.sif ./docking_process.sh convert csv/pairs.csv`

* **CSV Parsing and File Conversion**: The script reads the protein, ligand, and site information from the specified *CSV file*. It then converts PDB files to SDF format using *Open Babel*.

2. `singularity exec containers/gnina-1.0.sif ./docking_process.sh gnina <docking_method> csv/pairs.csv`

* **Docking**: Performs docking using the specified CNN scoring method using *GNINA*.
  - `none`: No CNN scoring is used. *(fastest, traditional)*
  - `rescore`: Rescoring using CNN. *(fastest with CNN)*
  - `refinement`: Refinement using CNN. *(moderate speed. 10x slower than rescore)*
  - `metrorescore`: Metropolis Monte Carlo sampling followed by rescoring using CNN.
  - `metrorefine`: Metropolis Monte Carlo sampling followed by refinement using CNN.
  - `all`: Ensemble of all CNN scoring methods are used. *(slowest, extremely computationally intensive)*

3. `singularity exec containers/python-3.12.sif ./docking_process.sh unzip`

* **Unzipping**: Unzips the docked results and stores them in the same directory.

4. `singularity exec containers/python-3.12.sif python docking_process.py --mode filter --filter_type <filter_type>`

* **Filtering**: Filters the docked results based on the specified filter type.
  - `all`: Retains all docked poses.
  - `best`: Retains the best docked pose based on the CNN score.

5. `singularity exec containers/openbabel-3.1.0.sif ./docking_process.sh sdftopdb`

* **SDF to PDB Conversion**: Converts the filtered SDF files to PDB format using *Open Babel*.

6. `singularity exec containers/python-3.12.sif python docking_process.py --mode combine --filter_type <filter_type> --csv_file csv/pairs.csv`

* **Combining Ligand and Protein**: Combines the best ligand conformation and given protein PDB files to generate a single PDB file.

7. `singularity exec containers/plip-1.0.sif ./docking_process.sh plip`

* **PLIP Processing**: Processes the combined PDB file using *PLIP* to identify interactions between the protein and ligand.

8. `singularity exec containers/python-3.12.sif python docking_process.py --mode report`

* **XML Processing**: Extracts the interactions from the PLIP XML file and generates a CSV file containing the interactions.

## Dependencies

- Python 3.11
- RDKit
- Singularity
- Open Babel
- GNINA
- PLIP

## SETUP

### Singularity installation

Run the shell script located in the link below
https://github.com/Mys7erio/scientiflow-singularity/blob/main/install-singularity.sh

### Python and OpenBabel containers installation using Singularity

`singularity pull containers/python-3.12.sif library://scientiflow/bioinformatics/python:3.12`

`singularity pull containers/openbabel-3.1.0.sif library://scientiflow/bioinformatics/openbabel:3.1.0`

`singularity pull containers/gnina-1.0.sif docker://gnina/gnina:latest`

`singularity pull plip.sif library://scientiflow/bioinformatics/plip:1.0`
