# Use openbabel to convert sdf to pdb files

import os

def sdf_to_pdb(sdf_file):
    os.system(f"singularity exec openbabel.sif obabel {sdf_file} -O {sdf_file.replace('.sdf', '.pdb')}")
