import os
import argparse
from rdkit import Chem

def get_sorted_mols(input_sdf):
    """Sort molecules by minimizedAffinity and CNNscore if available."""
    suppl = Chem.SDMolSupplier(input_sdf)
    valid_mols = [mol for mol in suppl if mol is not None]
    
    try:
        return sorted(
            valid_mols,
            key=lambda mol: (float(mol.GetProp('minimizedAffinity')), float(mol.GetProp('CNNscore')))
        )
    except Exception:
        print("No CNN score found, sorting by affinity only")
        return sorted(
            valid_mols,
            key=lambda mol: float(mol.GetProp('minimizedAffinity'))
        )

def save_molecules(mols, output_path, single_mol=False):
    """Save molecules to SDF file(s)."""
    output_dir = os.path.splitext(output_path)[0]
    os.makedirs(output_dir, exist_ok=True)
    
    if single_mol:
        output_file = os.path.join(output_dir, os.path.basename(output_path))
        writer = Chem.SDWriter(output_file)
        writer.write(mols[0])
    else:
        base_path = os.path.basename(output_path)
        for i, mol in enumerate(mols):
            output_file = os.path.join(output_dir, base_path.replace('.sdf', f'_{i}.sdf'))
            writer = Chem.SDWriter(output_file)
            writer.write(mol)
            writer.close()

def filter_docked(filter_type):
    """Process all SDF files in output folder."""
    for file in os.listdir("output"):
        if not file.endswith(".sdf"):
            continue
            
        input_file = os.path.join("output", file)
        sorted_mols = get_sorted_mols(input_file)
        
        if filter_type == "all":
            save_molecules(sorted_mols, input_file)
        else:  # filter_type == "best"
            save_molecules(sorted_mols, input_file.replace('.sdf', '_best.sdf'), single_mol=True)
            
        os.remove(input_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter docked conformations.')
    parser.add_argument('--filter_type', required=True, choices=['all', 'best'], 
                       help='Type of filtering to apply')
    
    args = parser.parse_args()
    filter_docked(args.filter_type)