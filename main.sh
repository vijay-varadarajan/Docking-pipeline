singularity exec containers/openbabel-3.1.0.sif ./convert_format.sh

singularity exec containers/gnina-1.0.sif ./gnina_docking.sh none

singularity exec containers/python-3.12.sif ./unzip.sh

singularity exec containers/python-3.12.sif python filter_docked.py --filter_type best

singularity exec containers/openbabel-3.1.0.sif ./sdf_to_pdb.sh

singularity exec containers/python-3.12.sif python combine_ligand_protein.py

singularity exec containers/plip-1.0.sif ./plip_processing.sh

singularity exec containers/python-3.12.sif python xml_processing.py