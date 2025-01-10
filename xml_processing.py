#report
import xml.etree.ElementTree as ET
import csv
import matplotlib.pyplot as plt
import os
from collections import defaultdict


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

def main():
    process_xml_files()
    
if __name__ == "__main__":
    main()