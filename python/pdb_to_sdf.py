# Use open babel to convert pdb to sdf files

import os

def pdb_to_sdf(pdb_file, openbabel_path):
    os.system(f"singularity exec {openbabel_path} obabel {pdb_file} -O {pdb_file.replace('.pdb', '.sdf')}")
    
if __name__ == "__main__":
    pdb_to_sdf("ligand/lig.pdb")
    pdb_to_sdf("sites/orig.pdb")