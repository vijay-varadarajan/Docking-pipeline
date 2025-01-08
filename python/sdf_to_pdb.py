# Use openbabel to convert sdf to pdb files

import os

def sdf_to_pdb(sdf_file, openbabel_path):
    os.system(f"singularity exec {openbabel_path} obabel {sdf_file} -O {sdf_file.replace('.sdf', '.pdb')}")
