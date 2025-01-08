from python.docking import traditional_docking, docking, whole_protein_docking
from filter_docked import filter_docked
from python.convert_2d_to_3d import convert_2d_to_3d
from python.pdb_to_sdf import pdb_to_sdf
from python.sdf_to_pdb import sdf_to_pdb

import os
import csv  
import argparse

BASE_FILE = os.path.expanduser("~/.scientiflow/config")

with open(BASE_FILE) as f:
    BASE_DIR = eval(f.readline())['BASE_DIR']
    print(BASE_DIR)

gnina_path = f"gnina.sif"
openbabel_path = f"{BASE_DIR}/containers/openbabel-3.1.0.sif"
python_path = f"{BASE_DIR}/containers/python-3.12.sif"


# Parse command line arguments
parser = argparse.ArgumentParser(description='Process docking parameters.')
parser.add_argument('-p', '--csv_path', type=str, required=True, help='Path to the CSV file')
parser.add_argument('-s', '--cnn_scoring', type=str, choices=['none', 'rescore', 'refinement', 'metrorescore', 'metrorefine', 'all'], default='rescore', help='CNN scoring method')
parser.add_argument('-f', '--filter_type', type=str, choices=["all", "best"], required=True, help='Filter type: "all" or "best"')
args = parser.parse_args()

results = "results"

# Read the protein, ligand, site from the csv file
with open(args.csv_path) as f:
    reader = csv.reader(f)
    next(reader)  # Skip the header row
    for i, row in enumerate(reader):
        protein, ligand, site = row

        ligand = "ligands/" + ligand.strip()
        site = "sites/" + site.strip()
        protein = "proteins/" + protein.strip()
        
        pdb_to_sdf(ligand, openbabel_path)
        print("Converted ligand to sdf")
        pdb_to_sdf(site, openbabel_path)
        print("Converted site to sdf")

        ligand = ligand.replace(".pdb", ".sdf")
        site = site.replace(".pdb", ".sdf")
        print(ligand, site, protein)

        cnn_scoring = args.cnn_scoring
        filter_type = args.filter_type

        os.system(f"mkdir -p {results}/{i}")
        docking(cnn_scoring, f"{ligand}", f"{site}", f"{protein}", f"{results}/{i}/cnn_{cnn_scoring}_docked.sdf.gz", gnina_path)
        
        os.system(f"gunzip {results}/{i}/cnn_{cnn_scoring}_docked.sdf.gz")
        
        filter_docked(filter_type, f"{results}/{i}/cnn_{cnn_scoring}_docked.sdf", f"{results}/{i}/cnn_{cnn_scoring}_docked_best.sdf")

        if filter_type == "best":
            sdf_to_pdb(f"{results}/{i}/cnn_{cnn_scoring}_docked_best.sdf", openbabel_path)
        else:
            os.system(f"mkdir -p {results}/{i}/all")
            for j in range(9):
                sdf_to_pdb(f"{results}/{i}/cnn_{cnn_scoring}_docked__{j}.sdf")
                os.system(f"mv {results}/{i}/cnn_{cnn_scoring}_docked__{j}.pdb {results}/{i}/all")