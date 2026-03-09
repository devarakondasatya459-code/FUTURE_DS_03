# =====================================
# Marketing Funnel Analysis
# =====================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

sns.set(style="whitegrid")

# =====================================
# 1. Load Dataset
# =====================================
df = pd.read_csv("marketing_funnel_data.csv")

# Inspect
print("First 5 rows:\n", df.head())
print("\nDataset Info:\n")
print(df.info())

# =====================================
# 2. Data Cleaning
# =====================================
# Convert date column if exists
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])

# Drop duplicates and missing critical data
df = df.drop_duplicates()
df = df.dropna(subset=['Lead ID', 'Funnel Stage', 'Channel'])

# Ensure Funnel Stage and Channel are string
df['Funnel Stage'] = df['Funnel Stage'].astype(str)
df['Channel'] = df['Channel'].astype(str)

# =====================================
# 3. Funnel Metrics
# =====================================
# Count unique leads per stage
funnel_counts = df.groupby('Funnel Stage')['Lead ID'].nunique().sort_values(ascending=False)
print("\nLeads per Funnel Stage:\n", funnel_counts)

# Stage-to-stage conversion %
conversion_rates = funnel_counts / funnel_counts.shift(1) * 100
conversion_rates = conversion_rates.fillna(100)  # top stage assumed 100%
print("\nStage-to-Stage Conversion Rates (%):\n", conversion_rates.round(2))

# Overall conversion
overall_conversion = funnel_counts.iloc[-1] / funnel_counts.iloc[0] * 100
print(f"\nOverall Funnel Conversion: {overall_conversion:.2f}%")

# =====================================
# 4. Channel Performance
# =====================================
# Leads per channel
channel_leads = df.groupby('Channel')['Lead ID'].nunique()

# Conversions per channel (assume bottom stage = 'Customer')
bottom_stage = df['Funnel Stage'].unique()[-1]
channel_conversions = df[df['Funnel Stage'] == bottom_stage].groupby('Channel')['Lead ID'].nunique()
channel_conversion_rate = (channel_conversions / channel_leads * 100).fillna(0)

channel_perf_df = pd.DataFrame({
    'Leads': channel_leads,
    'Conversions': channel_conversions,
    'Conversion Rate (%)': channel_conversion_rate.round(2)
}).sort_values(by='Conversion Rate (%)', ascending=False)

print("\nChannel Performance:\n", channel_perf_df)

# =====================================
# 5. Funnel Visualization (Plotly)
# =====================================
stages = funnel_counts.index.tolist()
values = funnel_counts.values.tolist()

fig = go.Figure(go.Funnel(
    y=stages,
    x=values,
    textinfo="value+percent initial"
))
fig.update_layout(title="Marketing Funnel Analysis")
fig.show()

# =====================================
# 6. Channel Performance Visualization
# =====================================
plt.figure(figsize=(10,6))
sns.barplot(x=channel_perf_df.index, y=channel_perf_df['Conversion Rate (%)'], palette="viridis")
plt.title("Channel Conversion Rates (%)")
plt.ylabel("Conversion Rate (%)")
plt.xlabel("Channel")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# =====================================
# 7. Drop-off Insights
# =====================================
dropoffs = 100 - conversion_rates
largest_drop_stage = dropoffs.idxmax()
print(f"\nLargest Conversion Drop-off at Stage: {largest_drop_stage} ({dropoffs.max():.2f}%)")

# =====================================
# 8. Export Summary
# =====================================
summary_df = pd.DataFrame({
    'Funnel Stage': funnel_counts.index,
    'Leads': funnel_counts.values,
    'Stage Conversion (%)': conversion_rates.round(2),
    'Drop-off (%)': dropoffs.round(2)
})
summary_df.to_csv("funnel_summary.csv", index=False)
channel_perf_df.to_csv("channel_performance.csv")
print("\nFunnel summary and channel performance exported as CSV files.")
