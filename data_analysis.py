import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# load The dataset
path_to_csv = 'All_Diets.csv';
df = pd.read_csv(path_to_csv);
#handle missing data (fill missing values with mean)
df.fillna(df.mean(numeric_only=True), inplace=True);
#calculate the average macronutrient content for each diet type 
avg_macros = df.groupby('Diet_type')[['Protein(g)', 'Carbs(g)', 'Fat(g)']].mean();
#Find the top 5 protein-rich recipes for each diet type
top_protein = df.sort_values('Protein(g)', ascending=False).groupby('Diet_type').head(5);
#Add new metrics (Protein-to-carbs ratio and Carbs-to-fats ratio)
df['Protein_to_Carbs_ratio'] = df['Protein(g)'] / df['Carbs(g)'];
df['Carbs_to_Fats_ratio'] = df['Carbs(g)'] / df['Fat(g)'];
# Bar chart for average macronutrients
sns.barplot(x=avg_macros.index, y=avg_macros['Protein(g)']);
plt.title('Average Protein by Diet Type');
plt.ylabel('Average Protein (g)');
plt.show();