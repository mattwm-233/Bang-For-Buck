import sqlite3
import pandas as pd
from analysis import master

conn = sqlite3.connect('bang_for_buck.db')
master.to_sql('master', conn, if_exists='replace', index=False)

# Average efficiency by league
avg_efficiency_query = """
SELECT League, 
       ROUND(AVG(Efficiency), 3) AS Avg_Efficiency,
       ROUND(AVG(Value_Z), 3) AS Avg_Value_Z,
       ROUND(AVG(Salary_Z), 3) AS Avg_Salary_Z
FROM master
GROUP BY League
ORDER BY Avg_Efficiency DESC;
"""

# Overpaid vs underpaid count by league
overpaid_query = """
SELECT League,
       SUM(CASE WHEN Efficiency > 0 THEN 1 ELSE 0 END) AS Outperforming,
       SUM(CASE WHEN Efficiency < 0 THEN 1 ELSE 0 END) AS Underperforming,
       COUNT(*) AS Total_Players
FROM master
GROUP BY League;
"""

# Salary tier analysis
salary_tier_query = """
SELECT League,
       CASE 
           WHEN Salary >= 50000000 THEN '$50M+'
           WHEN Salary >= 40000000 THEN '$40-50M'
           WHEN Salary >= 30000000 THEN '$30-40M'
           ELSE 'Under $30M'
       END AS Salary_Tier,
       ROUND(AVG(Efficiency), 3) AS Avg_Efficiency,
       COUNT(*) AS Players
FROM master
GROUP BY League, Salary_Tier
ORDER BY League, Salary_Tier;
"""

# Top 5 best value per league
best_value_query = """
SELECT League, Name, Salary, ROUND(Efficiency, 3) AS Efficiency
FROM master
ORDER BY League, Efficiency DESC;
"""

# Elite performers by Value_Z threshold
elite_query = """
SELECT League,
       SUM(CASE WHEN Value_Z >= 2 THEN 1 ELSE 0 END) AS Elite_Performers,
       SUM(CASE WHEN Value_Z BETWEEN 1 AND 2 THEN 1 ELSE 0 END) AS Above_Average,
       SUM(CASE WHEN Value_Z < 1 THEN 1 ELSE 0 END) AS Below_Average
FROM master
GROUP BY League;
"""

# Pct of total vs efficiency
cap_tier_query = """
SELECT League,
       CASE
           WHEN Pct_of_Total >= 20 THEN 'High %'
           WHEN Pct_of_Total >= 15 THEN 'Mid %'
           ELSE 'Low %'
       END AS Cap_Tier,
       ROUND(AVG(Efficiency), 3) AS Avg_Efficiency,
       COUNT(*) AS Players
FROM master
GROUP BY League, Cap_Tier
ORDER BY League, Cap_Tier;
"""

avg_efficiency = pd.read_sql_query(avg_efficiency_query, conn)
overpaid = pd.read_sql_query(overpaid_query, conn)
salary_tier = pd.read_sql_query(salary_tier_query, conn)
best_value = pd.read_sql_query(best_value_query, conn)
elite = pd.read_sql_query(elite_query, conn)
cap_tier = pd.read_sql_query(cap_tier_query, conn)

print('--- Average Efficiency by League ---')
print(avg_efficiency)
print('\n--- Outperforming vs Underperforming ---')
print(overpaid)
print('--- Salary Tier Analysis ---')
print(salary_tier)
print('\n--- Best Value Players by League ---')
print(best_value.groupby('League').head(5).to_string())
print('\n--- Elite Performers by League ---')
print(elite)
print('\n--- Cap % Tier vs Efficiency ---')
print(cap_tier)

conn.close()
