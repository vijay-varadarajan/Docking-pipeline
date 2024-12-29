import os
    
# with traditional docking
def traditional_docking(ligand_file, rec_file, orig_file, output_file):
    os.system(f"singularity exec gnina.sif gnina -l {ligand_file} -r {rec_file} --autobox_ligand {orig_file} -o {output_file} --cnn_scoring none")


# with default CNN scoring
def docking(cnn_scoring, ligand_file, orig_file, rec_file, output_file):
    os.system(f"singularity exec gnina.sif gnina -l {ligand_file} -r {rec_file} --autobox_ligand {orig_file} --cnn_scoring {cnn_scoring} -o {output_file}")
    print(f"singularity exec gnina.sif gnina -l {ligand_file} -r {rec_file} --autobox_ligand {orig_file} --cnn_scoring {cnn_scoring} -o {output_file}")


# whole protein docking
def whole_protein_docking(ligand_file, rec_file, output_file):
    os.system(f"singularity exec gnina.sif gnina -l {ligand_file} -r {rec_file} -o {output_file} --exhaustiveness 64")
    
    
if __name__ == "__main__":
    docking("rescore", "ligands/lig.sdf", "sites/orig.sdf", "proteins/rec.pdb", "results/cnn_rescore_docked.sdf")