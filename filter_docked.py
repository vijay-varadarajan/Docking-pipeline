import os
from rdkit import Chem

cnn_scoring = "rescore"

def extract_first_conformation(input_sdf, output_sdf):
    suppl = Chem.SDMolSupplier(input_sdf)
    writer = Chem.SDWriter(output_sdf)
    try:
        sorted_mols = sorted(
            (mol for mol in suppl if mol is not None),
            key=lambda mol: (float(mol.GetProp('minimizedAffinity')), float(mol.GetProp('CNNscore')))
        )
    except Exception as e:
        print("No CNN score found, sorting by affinity only")
        sorted_mols = sorted(
            (mol for mol in suppl if mol is not None),
            key=lambda mol: (float(mol.GetProp('minimizedAffinity')))
        )
        
    for mol in sorted_mols:
        writer.write(mol)
        break
    writer.close()
    

def extract_all_conformations(input_sdf, output_sdf):
    suppl = Chem.SDMolSupplier(input_sdf)
    try:
        sorted_mols = sorted(
            (mol for mol in suppl if mol is not None),
            key=lambda mol: (float(mol.GetProp('minimizedAffinity')), float(mol.GetProp('CNNscore')))
        )
    except Exception as e:
        print("No CNN score found, sorting by affinity only")
        sorted_mols = sorted(
            (mol for mol in suppl if mol is not None),
            key=lambda mol: (float(mol.GetProp('minimizedAffinity')))
        )
    for i, mol in enumerate(sorted_mols):
        if mol is not None:
            writer = Chem.SDWriter(output_sdf.replace('best.sdf', f'_{i}.sdf'))
            writer.write(mol)
            writer.close()


def filter_docked(arg, input_file, output_file):
    if arg == "all":
        extract_all_conformations(input_file, output_file)
    elif arg == "best":
        extract_first_conformation(input_file, output_file)
        
        
if __name__ == "__main__":
    filter_docked("all", "results/0/cnn_rescore_docked.sdf", "results/0/cnn_rescore_docked_best.sdf")
    