import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from collections import defaultdict
import os
import argparse
from rdkit import Chem
import csv
import sys

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

def process_csv(csv_file, type="best"):
    if type == "best":
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
    else:
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                ligand_file, protein_file, site_file = row
                ligand_base = os.path.splitext(ligand_file)[0]
                protein_base = os.path.splitext(protein_file)[0]
                site_base = os.path.splitext(site_file)[0]
                
                ligand_folder_path = f"output/{ligand_base}_{protein_base}_{site_base}/"
                for file in os.listdir(ligand_folder_path):
                    if file.endswith(".pdb"):
                        ligand_pdb_path = os.path.join(ligand_folder_path, file)
                        protein_pdb_path = f"proteins/{protein_file}"
                        output_pdb_path = f"output/{ligand_base}_{protein_base}_{site_base}/combined_{file}"
                        if os.path.exists(protein_pdb_path):
                            combine_protein_ligand(protein_pdb_path, ligand_pdb_path, output_pdb_path)
                        else:
                            print(f"Missing files for {ligand_base}_{protein_base}_{site_base}, skipping...")
                            
def combine_protein_ligand_util(csv_file, type):
    process_csv(csv_file, type)
    


def process_xml_files():
    
    folder = "output/"
    xml_files = []
    
    for fold in os.listdir(folder):
        fold_path = os.path.join(folder, fold)
        if os.path.isdir(fold_path):
            xml_files += [os.path.join(fold_path, file) for file in os.listdir(fold_path) if file.endswith(".xml")]
    if not xml_files:
        print("No XML files found in the specified folder.")
        return
    
    # Initialize variables
    interactions_categories = set()
    data = []

    # Process each XML file
    for file in xml_files:
        file_name = os.path.basename(file)
        tree = ET.parse(file)
        root = tree.getroot()

        interaction_counts = defaultdict(int)

        # Count interactions
        for interaction_category in root.findall(".//interactions/*"):
            category_name = interaction_category.tag
            interactions_categories.add(category_name)
            interaction_counts[category_name] += len(interaction_category.findall("*"))

        data.append((file_name, interaction_counts))

    # Prepare CSV file
    csv_filename = f"output/excel_interaction_report.csv"

    # Custom order: First three categories, then the rest
    first_three = ["hydrogen_bonds", "hydrophobic_interactions", "salt_bridges"]
    rest_categories = sorted(set(interactions_categories) - set(first_three))
    csv_headers = ["complex_name"] + first_three + rest_categories

    # Write CSV file
    with open(csv_filename, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(csv_headers)
        for file_name, interaction_counts in data:
            row = [file_name]
            for category in csv_headers[1:]:  # Skip 'complex_name'
                row.append(interaction_counts.get(category, 0))
            writer.writerow(row)

    # Plotting
    category_colors = plt.get_cmap("tab10", len(interactions_categories))

    for i, category in enumerate(csv_headers[1:]):  # Skip 'complex_name'
        y = [d[1].get(category, 0) for d in data]

        # Only plot if at least one value is greater than 0
        if any(value > 0 for value in y):
            x = [d[0] for d in data]
            plt.plot(x, y, label=category, color=category_colors(i))

    # Customize plot
    plt.xlabel("File Name")
    plt.ylabel("Number of Interactions")
    plt.title("Interactions by Category")
    plt.xticks(rotation=45, ha="right")

    # Move legend outside the plot
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), title="Interaction Types")

    # Adjust spacing to make room for the legend
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust plot to leave space for the legend

    # Save the plot as a file
    plot_filename = f"output/plot_interaction_report.png"
    plt.savefig(plot_filename, bbox_inches="tight")
    plt.show()
    print(f"Plot saved as {plot_filename}")

def process_xml_files_util():
    process_xml_files()
    

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

def filter_docked_util(filter_type):
    filter_docked(filter_type)


def main():
    parser = argparse.ArgumentParser(description='Docking process pipeline.')
    parser.add_argument('--mode', required=True, choices=['combine', 'filter', 'report'],
                        help='Mode to run: combine, filter, report')
    parser.add_argument('--filter_type', choices=['all', 'best'], help='Type of filter for combine or filter mode')
    parser.add_argument('--csv_file', help='CSV file for combine mode')
    
    args = parser.parse_args()
    
    if args.mode == 'combine':
        if not args.csv_file or not args.filter_type:
            print("For combine mode, --csv_file and --filter_type are required.")
            sys.exit(1)
        combine_protein_ligand_util(args.csv_file, args.filter_type)
    elif args.mode == 'filter':
        if not args.filter_type:
            print("For filter mode, --filter_type is required.")
            sys.exit(1)
        filter_docked_util(args.filter_type)
    elif args.mode == 'report':
        process_xml_files_util()

if __name__ == "__main__":
    main()
