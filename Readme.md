# 📊 Dataset Analysis and Insights (Task 1)

## 👨‍💻 Project Overview

This project analyzes a dietary dataset using Python (Pandas, Matplotlib, Seaborn) in an Ubuntu VM environment.  
The goal is to extract nutritional insights and visualize key patterns across different diet types.

## 🎯 Objectives

- Calculate average macronutrient content (Protein, Carbs, Fat) for each diet type  
- Identify top 5 protein-rich recipes per diet type  
- Find the diet type with the highest protein content  
- Identify most common cuisines per diet type  
- Create new nutritional metrics:
  - Protein-to-Carbs ratio  
  - Carbs-to-Fat ratio  
- Clean dataset by handling missing values  
- Visualize results using charts  

## 📁 Project Structure

project/
│
├── All_Diets.csv
├── data_analysis.py
├── README.md
├── requirements.txt
│
└── outputs/
    ├── bar_chart.png
    ├── heatmap.png
    └── scatter_plot.png

## ⚙️ Setup Instructions (After Cloning Repo)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/HenryPhan05/Project1
cd Project1
2️⃣ Create Virtual Environment (Recommended)
python3 -m venv .venv

Activate it:

Linux / Ubuntu:

source .venv/bin/activate

Windows (PowerShell):

.venv\Scripts\Activate.ps1
3️⃣ Install Required Libraries
pip install -r requirements.txt

If requirements.txt is missing:

pip install pandas matplotlib seaborn numpy
4️⃣ Run the Analysis Script
python data_analysis.py
📊 What the Script Does
Data Cleaning
Fill missing numeric values with column mean
Analysis
Average Protein, Carbs, Fat by diet type
Top 5 protein-rich recipes per diet type
Most common cuisine per diet type
Highest protein recipe overall
Feature Engineering
Protein-to-Carbs ratio
Carbs-to-Fat ratio
📈 Visualizations
Bar Chart → Average macronutrients per diet type
Heatmap → Relationship between nutrients and diet types
Scatter Plot → Top protein recipes across cuisines

Saved in /outputs folder.

📦 Requirements

Create requirements.txt:

pandas
numpy
matplotlib
seaborn

🖼️ Screenshots Requirement
VS Code running code
Terminal output
Generated graphs
System date & time visible (important for grading)
