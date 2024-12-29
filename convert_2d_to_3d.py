import os

def convert_2d_to_3d(file_2d):
    os.system(f"singularity exec openbabel.sif obabel -isdf {file_2d} -osdf -O {file_2d.replace('.sdf', '_3d.sdf')} --gen3d")
    
if __name__ == "__main__":
    convert_2d_to_3d("ligands/lig.sdf")
    convert_2d_to_3d("sites/orig.sdf")