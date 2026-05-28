import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def clean_currency(df, columns):
    for col in columns:
        df[col] = (df[col]
                   .str.replace('$', '', regex=False)
                   .str.replace(',', '', regex=False)
                   .str.strip()
                   .astype(float))
    return df

leagues = ['MLB', 'NBA', 'NFL']
league_totals = pd.read_csv('league_salary_totals.csv')
league_totals = clean_currency(league_totals, ['TotalPay', 'AvgPay'])

mlb_salaries = pd.read_csv('MLB_Salary_2025.csv')
nba_salaries = pd.read_csv('NBA_Salary_2025.csv')
nfl_salaries = pd.read_csv('NFL_Salary_2025.csv')

mlb_payroll = mlb_salaries[['Name', 'AAV', 'Payroll %']].sort_values(by='Payroll %', ascending=False)
nba_payroll = nba_salaries[['Name', 'Cap Hit', 'Cap %']].sort_values(by='Cap %', ascending=False)
nfl_payroll = nfl_salaries[['Name', 'Cap Hit', 'Cap %']].sort_values(by='Cap %', ascending=False)

mlb_top20 = mlb_payroll.rename(columns={'AAV': 'Salary', 'Payroll %': 'Pct_of_Total'}).assign(League='MLB')
nba_top20 = nba_payroll.rename(columns={'Cap Hit': 'Salary', 'Cap %': 'Pct_of_Total'}).assign(League='NBA')
nfl_top20 = nfl_payroll.rename(columns={'Cap Hit': 'Salary', 'Cap %': 'Pct_of_Total'}).assign(League='NFL')

mlb_top20 = clean_currency(mlb_top20, ['Salary'])
nba_top20 = clean_currency(nba_top20, ['Salary'])
nfl_top20 = clean_currency(nfl_top20, ['Salary'])

top_paid = pd.concat([mlb_top20, nba_top20, nfl_top20], ignore_index=True)

top20_merged = top_paid.merge(league_totals, on='League', how='left')

# How many times more than the average player each top 20 player earns
top20_merged['Vs_Avg'] = top20_merged['Salary'] / top20_merged['AvgPay']

# Each player's individual % of total league payroll
top20_merged['Pct_of_League'] = (top20_merged['Salary'] / top20_merged['TotalPay']) * 100

# How much the top 20 collectively consume per league
top20_concentration = top20_merged.groupby('League').agg(
    Top20_Total=('Salary', 'sum'),
    Total_Payroll=('TotalPay', 'first'),
    Avg_Salary=('AvgPay', 'first'),
    Players=('Players', 'first')
).assign(Top20_Pct=lambda x: (x['Top20_Total'] / x['Total_Payroll']) * 100)

top20_concentration['Top20_Total'] = top20_concentration['Top20_Total'].map('${:,.0f}'.format)
top20_concentration['Total_Payroll'] = top20_concentration['Total_Payroll'].map('${:,.0f}'.format)
top20_concentration['Avg_Salary'] = top20_concentration['Avg_Salary'].map('${:,.0f}'.format)
top20_concentration['Top20_Pct'] = top20_concentration['Top20_Pct'].map('{:.2f}%'.format)

plt.figure(figsize=(8, 5))
leagues = top20_concentration.index
pcts = top20_concentration['Top20_Pct'].str.replace('%', '').astype(float)
colors = ['#1f77b4', '#ff7f0e', '#d62728']
bars = plt.bar(leagues, pcts, color=colors, width=0.5)
# Add value labels on top of each bar
for bar, pct in zip(bars, pcts):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.2,
        f'{pct:.2f}%',
        ha='center',
        va='bottom',
        fontsize=11,
        fontweight='bold'
    )

plt.title('Top 20 Player Salaries as % of Total League Payroll (2025)', fontsize=13)
plt.xlabel('League')
plt.ylabel('% of Total Payroll')
plt.ylim(0, 25)
plt.tight_layout()


fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)

leagues = {
    'MLB': (mlb_top20, '#1f77b4'),
    'NBA': (nba_top20, '#ff7f0e'),
    'NFL': (nfl_top20, '#d62728')
}

for ax, (league, (data, color)) in zip(axes, leagues.items()):
    sns.barplot(
        data=data,
        x='Name',
        y='Pct_of_Total',
        color=color,
        ax=ax
    )
    ax.set_title(f'{league} Top 20 Salaries (2025)')
    ax.set_xlabel('')
    ax.set_ylabel('% of Total Payroll / Cap' if ax == axes[0] else '')
    ax.tick_params(axis='x', rotation=45)
    ax.set_xticklabels(ax.get_xticklabels(), ha='right', fontsize=9)

plt.suptitle('Top 20 Highest Paid Players by % of Total Payroll/Cap (2025)', 
             fontsize=14, y=1.02)
plt.tight_layout()


plt.figure(figsize=(12, 6))

sns.barplot(
    data=top_paid,
    x='Name',
    y='Pct_of_Total',
    hue='League',
    palette={'MLB': '#1f77b4', 'NBA': '#ff7f0e', 'NFL': '#d62728'}
)

plt.title('Top 20 Highest Paid Players by % of Total Payroll/Cap (2025)')
plt.xlabel('Player')
plt.ylabel('% of Total Payroll / Cap')
plt.xticks(rotation=45, ha='right')
plt.legend(title='League')
plt.tight_layout()


if __name__ == "__main__":
    plt.show()
    print(mlb_top20)
    print(nba_top20)
    print(nfl_top20)
