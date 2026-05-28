import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# MLB stats:
batting_stats = pd.read_csv('MLB_bstats_2025.csv')
fielding_stats = pd.read_csv('MLB_fvalue_2025.csv')
pitching_stats = pd.read_csv('MLB_pvalue_2025.csv')

position_players = batting_stats.merge(
    fielding_stats[['Name', 'Team', 'Pos', 'dWAR', 'Rtot', 'Fld%']],
    on='Name',
    how='left'
)

position_players['dWAR'] = position_players['dWAR'].fillna(0)

pitchers = pitching_stats[['Name', 'Team', 'IP', 'WAR']].rename(columns={'WAR': 'Total_WAR'})
pitcher_names = pitching_stats['Name'].tolist()
two_way = ['Shohei Ohtani']

pos_players_clean = position_players[
    (~position_players['Name'].isin(pitcher_names)) | 
    (position_players['Name'].isin(two_way))
][['Name', 'Team', 'Pos', 'oWAR', 'dWAR', 'Total_WAR', 'OPS']]

ohtani_pitching_war = pitchers.loc[pitchers['Name'] == 'Shohei Ohtani', 'Total_WAR'].values[0]

pos_players_clean.loc[pos_players_clean['Name'] == 'Shohei Ohtani', 'Total_WAR'] += ohtani_pitching_war

pitchers_clean = pitchers[~pitchers['Name'].isin(two_way)]

mlb_value = pd.concat([pos_players_clean, pitchers_clean], ignore_index=True)
mlb_value['Pos'] = mlb_value['Pos'].fillna('SP')

plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=mlb_value,
    x='Name',
    y='Total_WAR',
    hue='Pos',
    palette='tab10',
    s=100
)

plt.title('Total WAR by Position - MLB Top 20 Paid Players (2025)', fontsize=13)
plt.xlabel('')
plt.ylabel('Total WAR')
plt.xticks(rotation=45, ha='right', fontsize=9)
plt.axhline(y=0, color='red', linestyle='--', linewidth=0.8, alpha=0.7)
plt.legend(title='Position', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()


# NBA stats:
nba_value = pd.read_csv('NBA_value_2025.csv')

# Plot 1 - DPM by player colored by position
plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=nba_value,
    x='Name',
    y='DPM',
    hue='Position',
    palette='tab10',
    s=100
)

plt.title('DPM by Position - NBA Top 20 Paid Players (2025)', fontsize=13)
plt.xlabel('')
plt.ylabel('Daily Plus-Minus (DPM)')
plt.xticks(rotation=45, ha='right', fontsize=9)
plt.axhline(y=0, color='red', linestyle='--', linewidth=0.8, alpha=0.7)
plt.legend(title='Position', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()


# Plot 2 - DPM vs OB% colored by position
plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=nba_value,
    x='OB%',
    y='DPM',
    hue='Position',
    palette='tab10',
    s=100
)

for _, row in nba_value.iterrows():
    plt.annotate(
        row['Name'].split()[-1],
        (row['OB%'], row['DPM']),
        textcoords='offset points',
        xytext=(5, 5),
        fontsize=8
    )

plt.title('DPM vs Usage Rate (OB%) - NBA Top 20 Paid Players (2025)', fontsize=13)
plt.xlabel('On-Ball Percentage / Usage Rate (OB%)')
plt.ylabel('Daily Plus-Minus (DPM)')
plt.axhline(y=0, color='red', linestyle='--', linewidth=0.8, alpha=0.7)
plt.legend(title='Position', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

# NFL stats:
nfl_offense = pd.read_csv('NFL_ovalue_2025.csv')
nfl_defense = pd.read_csv('NFL_dvalue_2025.csv')

# Recalculate EPA/P for receivers where it shows 0 but EPA exists
nfl_offense['EPA/P'] = nfl_offense.apply(
    lambda row: None if row['EPA'] == 0
    else row['EPA/P'],
    axis=1
)

# Flag injured/DNP players
nfl_offense['DNP'] = nfl_offense['GP'] == 0

# Normalize defensive stats into a simple pressure score
nfl_defense['EPA'] = None
nfl_defense['EPA/P'] = None
nfl_defense['Position'] = 'DL'

# Pressure rate as a proxy value metric for defenders
nfl_defense['Press_Rate'] = nfl_defense['Prss'] / nfl_defense['G']

# Add position to offense based on stats
nfl_offense['Position'] = nfl_offense.apply(
    lambda row: 'DNP' if row['GP'] == 0
    else 'QB' if row['pYds'] > 0
    else 'WR' if row['recYds'] > 0
    else 'RB',
    axis=1
)

nfl_offense['Press_Rate'] = None

# Align columns before combining
shared_cols = ['Name', 'Team', 'Position', 'GP', 'EPA', 'EPA/P', 'Press_Rate']

nfl_offense_clean = nfl_offense.rename(columns={'GP': 'GP'})[shared_cols]
nfl_defense_clean = nfl_defense.rename(columns={'G': 'GP'})[shared_cols]

nfl_value = pd.concat([nfl_offense_clean, nfl_defense_clean], ignore_index=True)
nfl_active = nfl_value[(nfl_value['EPA'].notna()) & (nfl_value['EPA'] != 0)]

plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=nfl_active,
    x='Name',
    y='EPA',
    hue='Position',
    palette='tab10',
    s=100
)

plt.title('EPA by Position - NFL Top 20 Paid Players (2025)', fontsize=13)
plt.xlabel('')
plt.ylabel('Expected Points Added (EPA)')
plt.xticks(rotation=45, ha='right', fontsize=9)
plt.axhline(y=0, color='red', linestyle='--', linewidth=0.8, alpha=0.7)
plt.legend(title='Position', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()


if __name__ == "__main__":
    plt.show()
    print(mlb_value)
    print(nba_value)
    print(nfl_value)
