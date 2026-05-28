import pandas as pd

#  MLB -- Comparison to leage average WAR
league_bWAR = pd.read_csv('WAR_hitters.csv')
league_pWAR = pd.read_csv('WAR_pitchers.csv')

league_bWAR_clean = league_bWAR[['Player', 'WAR']].rename(columns={'WAR': 'Total_WAR'})
league_pWAR_clean = league_pWAR[['Player', 'WAR']].rename(columns={'WAR': 'Total_WAR'})

# Handle Ohtani
ohtani_pWAR = league_pWAR_clean.loc[league_pWAR_clean['Player'].str.contains('Ohtani'), 'Total_WAR'].values[0]
league_pWAR_clean = league_pWAR_clean[~league_pWAR_clean['Player'].str.contains('Ohtani')]
league_bWAR_clean.loc[league_bWAR_clean['Player'].str.contains('Ohtani'), 'Total_WAR'] += ohtani_pWAR

qualified_hitters = league_bWAR_clean[league_bWAR['PA'] >= 100]
qualified_pitchers = league_pWAR_clean[league_pWAR['IP'] >= 20]

league_WAR_qualified = pd.concat([qualified_hitters, qualified_pitchers], ignore_index=True)
war_mean = league_WAR_qualified['Total_WAR'].mean()
war_std = league_WAR_qualified['Total_WAR'].std()

# print(f'League WAR Mean: {war_mean:.3f}')
# print(f'League WAR Std: {war_std:.3f}')
# print(f'Total Players: {len(league_WAR_qualified)}')

# NBA -- Comparison to league average BPM
league_BPM = pd.read_csv('NBA_BPM.csv')
nba_qualified = league_BPM[league_BPM['MP'] >= 500]
bpm_mean = nba_qualified['BPM'].mean()
bpm_std = nba_qualified['BPM'].std()

# print(f'League BPM Mean: {bpm_mean:.3f}')
# print(f'League BPM Std: {bpm_std:.3f}')
# print(f'Total Players: {len(nba_qualified)}')

# NFL -- Comparison to league average EPA
nfl_stats_2025 = pd.read_csv('NFL_stats_2025.csv')

# Filter to regular season only
nfl_league = nfl_stats_2025[nfl_stats_2025['season_type'] == 'REG']

# Skill positions only for EPA baseline
skill_positions = ['QB', 'RB', 'WR', 'TE']
nfl_skill = nfl_league[nfl_league['position_group'].isin(skill_positions)]

# Calculate EPA per play for each position group
def calc_epa_per_play(row):
    if row['position_group'] == 'QB' and row['attempts'] > 0:
        return (row['passing_epa'] + row['rushing_epa']) / (row['attempts'] + row['carries'])
    elif row['position_group'] == 'RB' and row['carries'] > 0:
        return (row['rushing_epa'] + row['receiving_epa']) / (row['carries'] + row['receptions'])
    elif row['position_group'] in ['WR', 'TE'] and row['targets'] > 0:
        return row['receiving_epa'] / row['targets']
    else:
        return None

nfl_skill = nfl_skill.copy()
nfl_skill['EPA_per_play'] = nfl_skill.apply(calc_epa_per_play, axis=1)

# Qualify by games and minimum touches to avoid small sample noise
nfl_qualified = nfl_skill[
    (nfl_skill['EPA_per_play'].notna()) &
    (nfl_skill['games'] >= 4)
]

epa_pp_mean = nfl_qualified['EPA_per_play'].mean()
epa_pp_std = nfl_qualified['EPA_per_play'].std()

# print(f'League EPA/Play Mean: {epa_pp_mean:.3f}')
# print(f'League EPA/Play Std: {epa_pp_std:.3f}')
# print(f'Total Players: {len(nfl_qualified)}')
