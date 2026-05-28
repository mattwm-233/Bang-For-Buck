from salary import mlb_top20, nba_top20, nfl_top20
from value import mlb_value, nba_value, nfl_value
from league_totals import war_mean, war_std, bpm_mean, bpm_std, epa_pp_mean, epa_pp_std
from scipy import stats
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Jawaan Taylor has no value data so drop him from NFL salary table
nfl_top20 = nfl_top20[nfl_top20['Name'] != 'Jawaan Taylor']

# Merge salary and value tables
mlb_combined = mlb_top20.merge(mlb_value, on='Name', how='left')
nba_combined = nba_top20.merge(nba_value, on='Name', how='left')
nfl_combined = nfl_top20.merge(nfl_value, on='Name', how='left')

nfl_combined['EPA'] = pd.to_numeric(nfl_combined['EPA'], errors='coerce')
nfl_combined['Press_Rate'] = pd.to_numeric(nfl_combined['Press_Rate'], errors='coerce')

# MLB Z-scores
mlb_active = mlb_combined[mlb_combined['Total_WAR'].notna()].copy()
mlb_active['Value_Z'] = (mlb_active['Total_WAR'] - war_mean) / war_std
mlb_active['Salary_Z'] = stats.zscore(mlb_active['Salary'])
mlb_active['Efficiency'] = mlb_active['Value_Z'] - mlb_active['Salary_Z']

# NBA Z-scores
nba_active = nba_combined[nba_combined['BPM'].notna()].copy()
nba_active['Value_Z'] = (nba_active['BPM'] - bpm_mean) / bpm_std
nba_active['Salary_Z'] = stats.zscore(nba_active['Salary'])
nba_active['Efficiency'] = nba_active['Value_Z'] - nba_active['Salary_Z']

# NFL Z-scores
nfl_active = nfl_combined[
    (nfl_combined['EPA/P'].notna()) &
    (nfl_combined['EPA/P'] != 0) &
    (nfl_combined['Position'] != 'DNP') &
    (nfl_combined['Position'] != 'DL')
].copy()
nfl_active['Value_Z'] = (nfl_active['EPA/P'] - epa_pp_mean) / epa_pp_std
nfl_active['Salary_Z'] = stats.zscore(nfl_active['Salary'])
nfl_active['Efficiency'] = nfl_active['Value_Z'] - nfl_active['Salary_Z']

# Stack into master DataFrame
master = pd.concat([
    mlb_active[['Name', 'League', 'Salary', 'Pct_of_Total', 'Value_Z', 'Salary_Z', 'Efficiency']],
    nba_active[['Name', 'League', 'Salary', 'Pct_of_Total', 'Value_Z', 'Salary_Z', 'Efficiency']],
    nfl_active[['Name', 'League', 'Salary', 'Pct_of_Total', 'Value_Z', 'Salary_Z', 'Efficiency']]
], ignore_index=True)

print(master.sort_values('Efficiency', ascending=False).to_string())

master_sorted = master.sort_values('Efficiency', ascending=True).reset_index(drop=True)

colors = master_sorted['League'].map({'MLB': '#1f77b4', 'NBA': '#ff7f0e', 'NFL': '#d62728'})

fig, ax = plt.subplots(figsize=(10, 14))

ax.barh(master_sorted['Name'], master_sorted['Efficiency'], color=colors)

ax.axvline(x=0, color='black', linestyle='--', linewidth=0.8)
ax.set_title('Salary Efficiency by Player (2025)\nValue Z-Score minus Salary Z-Score', fontsize=13)
ax.set_xlabel('Efficiency Score')

from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#1f77b4', label='MLB'),
    Patch(facecolor='#ff7f0e', label='NBA'),
    Patch(facecolor='#d62728', label='NFL')
]
ax.legend(handles=legend_elements, loc='lower right')
plt.tight_layout()
plt.show()

# Scatter plot to compare leagues
plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=master,
    x='Salary_Z',
    y='Value_Z',
    hue='League',
    palette={'MLB': '#1f77b4', 'NBA': '#ff7f0e', 'NFL': '#d62728'},
    s=100
)

# Reference lines for average salary and average value
plt.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.7)
plt.axvline(x=0, color='black', linestyle='--', linewidth=0.8, alpha=0.7)

plt.title('Value Z-Score vs Salary Z-Score by League (2025)', fontsize=13)
plt.xlabel('Salary Z-Score')
plt.ylabel('Value Z-Score')
plt.legend(title='League')
plt.tight_layout()
plt.show()