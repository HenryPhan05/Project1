import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os 
print("=================================")
print("STARTING DATA ANALYSIS")
print("=================================")
# load The dataset
print("Start Running analysis...")
path_to_csv = 'All_Diets.csv';
df = pd.read_csv(path_to_csv);
print(f"\nDataset loaded successfully.")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")
#handle missing data (fill missing values with mean)
df.fillna(df.mean(numeric_only=True), inplace=True);
print("\nMissing values handled.")
#calculate the average macronutrient content for each diet type 
avg_macros = df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean();
print("\n=================================")
print("AVERAGE MACRONUTRIENTS")
print("=================================")
print(avg_macros)
#save results 
avg_macros.to_csv("average_macros.csv")
#Find the top 5 protein-rich recipes for each diet type
top_protein = df.sort_values('Protein(g)', ascending=False).groupby('Diet_type').head(5);
print("\n=================================")
print("TOP 5 PROTEIN-RICH RECIPES")
print("=================================")

print(
    top_protein[
        ["Diet_type", "Recipe_name", "Protein(g)"]
    ]
)
# -----------------------------------
# MOST COMMON CUISINE
# -----------------------------------

common_cuisine = (
    df.groupby("Diet_type")["Cuisine_type"]
      .agg(lambda x: x.mode()[0])
)
print("\n=================================")
print("MOST COMMON CUISINE BY DIET TYPE")
print("=================================")
print(common_cuisine)

common_cuisine.to_csv("common_cuisine.csv")

top_protein.to_csv("top_protein_recipes.csv", index=False)
#Add new metrics (Protein-to-carbs ratio and Carbs-to-fats ratio)
df['Protein_to_Carbs_ratio'] = df['Protein(g)'] / df['Carbs(g)'];
df['Carbs_to_Fats_ratio'] = df['Carbs(g)'] / df['Fat(g)'];
print("\nNew metrics created.")

# -----------------------------------
# CREATE OUTPUT FOLDER
# -----------------------------------

os.makedirs("charts", exist_ok=True)
# -----------------------------------
# BAR CHART
# -----------------------------------
# Bar chart for average macronutrients

plt.figure(figsize=(10, 6))

sns.barplot(
    x=avg_macros.index,
    y=avg_macros["Protein(g)"]
)
plt.title("Average Protein by Diet Type")
plt.ylabel("Average Protein (g)")
plt.xlabel("Diet Type")
plt.tight_layout()

plt.savefig("charts/bar_chart_protein.png")

plt.close()

print("Bar chart saved.")

# -----------------------------------
# HEATMAP
# -----------------------------------
plt.figure(figsize=(10, 6))

sns.heatmap(
    avg_macros,
    annot=True,
    cmap="YlGnBu"
)

plt.title("Macronutrient Heatmap")

plt.tight_layout()

plt.savefig("charts/heatmap_macros.png")

plt.close()

print("Heatmap saved.");


# -----------------------------------
# SCATTER PLOT
# -----------------------------------

plt.figure(figsize=(12, 8))

sns.scatterplot(
    data=top_protein,
    x="Protein(g)",
    y="Carbs(g)",
    hue="Cuisine_type"
)

plt.title("Top Protein-Rich Recipes by Cuisine")

plt.tight_layout()

plt.savefig("charts/scatter_top_protein.png")

plt.close()

print("Scatter plot saved.")

print("\n=================================")
print("ANALYSIS COMPLETE")
print("=================================")

print("\nGenerated files:")
print("- average_macros.csv")
print("- top_protein_recipes.csv")
print("- common_cuisine.csv")
print("- charts/bar_chart_protein.png")
print("- charts/heatmap_macros.png")
print("- charts/scatter_top_protein.png")
