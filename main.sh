singularity exec containers/openbabel-3.1.0.sif ./docking_process.sh convert csv/pairs.csv

singularity exec containers/gnina-1.0.sif ./docking_process.sh gnina none csv/pairs.csv

singularity exec containers/python-3.12.sif ./docking_process.sh unzip 

singularity exec containers/python-3.12.sif python docking_process.py --mode filter --filter_type best

singularity exec containers/openbabel-3.1.0.sif ./docking_process.sh sdftopdb

singularity exec containers/python-3.12.sif python docking_process.py --mode combine --filter_type best --csv_file csv/pairs.csv

singularity exec containers/plip-1.0.sif ./docking_process.sh plip

singularity exec containers/python-3.12.sif python docking_process.py --mode report 