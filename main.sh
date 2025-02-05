singularity exec containers/gnina-1.0.sif ./docking_process.sh --mode gnina --cnn_scoring none --input_file csv/pairs.csv --blind 0 --exhaustiveness 8 --num_modes 9

singularity exec containers/python-3.12.sif ./docking_process.sh --mode unzip

singularity exec containers/python-3.12.sif python docking_process.py --mode filter --filter_type all --input_file csv/pairs.csv

singularity exec containers/openbabel-3.1.0.sif ./docking_process.sh --mode sdftopdb

singularity exec containers/python-3.12.sif python docking_process.py --mode combine --filter_type all --input_file csv/pairs.csv

singularity exec containers/plip-1.0.sif ./docking_process.sh --mode plip

singularity exec containers/python-3.12.sif python docking_process.py --mode report 