from rdkit import Chem
import csv
import os

def combine_protein_ligand(protein_pdb_file, ligand_pdb_file, output_pdb_file):
    # Load the protein and ligand structures
    protein_mol = Chem.MolFromPDBFile(protein_pdb_file, removeHs=False)
    ligand_mol = Chem.MolFromPDBFile(ligand_pdb_file, removeHs=False)

    if not protein_mol:
        raise ValueError(f"Failed to read the protein file: {protein_pdb_file}")
    if not ligand_mol:
        raise ValueError(f"Failed to read the ligand file: {ligand_pdb_file}")

    # Combine the two molecules
    combined_mol = Chem.CombineMols(protein_mol, ligand_mol)

    # Write the combined structure to a new PDB file
    with Chem.rdmolfiles.PDBWriter(output_pdb_file) as writer:
        writer.write(combined_mol)

    print(f"Combined structure saved to: {output_pdb_file}")

def process_csv(csv_file):
    with open(csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            ligand_file, protein_file, site_file = row
            ligand_base = os.path.splitext(ligand_file)[0]
            protein_base = os.path.splitext(protein_file)[0]
            site_base = os.path.splitext(site_file)[0]
            
            combined_name = f"{ligand_base}_{protein_base}_{site_base}_best.pdb"
            ligand_pdb_path = f"output/{ligand_base}_{protein_base}_{site_base}_best/{combined_name}"
            protein_pdb_path = f"proteins/{protein_file}"
            output_pdb_path = f"output/{ligand_base}_{protein_base}_{site_base}_best/combined_{combined_name}"
            
            if os.path.exists(ligand_pdb_path) and os.path.exists(protein_pdb_path):
                combine_protein_ligand(protein_pdb_path, ligand_pdb_path, output_pdb_path)
            else:
                print(f"Missing files for {combined_name}, skipping...")

if __name__ == "__main__":
    csv_file = "csv/pairs.csv"
    process_csv(csv_file)

