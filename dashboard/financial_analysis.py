import pandas as pd
from sklearn.cluster import KMeans
import numpy as np

def get_savings_suggestions(transactions):
    suggestions = {}
    grouped = transactions.groupby('payee_type')['amount'].sum()
    for category, amount in grouped.items():
        if amount > 1000:  # Example threshold
            suggestions[category] = amount * 0.1  # Suggest 10% savings
    return suggestions
#-------------------------------------------------------------------------------------------------------------------

def compare_spending(transactions):
    monthly = transactions.groupby(transactions['date'].dt.to_period('M'))['amount'].sum().reset_index()
    monthly['date'] = monthly['date'].astype(str)
    return monthly.to_dict(orient='records')
#-------------------------------------------------------------------------------------------------------------------

def cash_flow_analysis(credit_df, debit_df):
    # Inflows: Total sum of credit amounts
    inflows = credit_df['amount'].sum()
    
    # Outflows: Total sum of debit amounts
    outflows = debit_df['amount'].sum()
    
    return inflows, abs(outflows)

#-------------------------------------------------------------------------------------------------------------------

def spending_alerts(transactions):
    alerts = []
    for _, row in transactions.iterrows():
        if row['amount'] > 50000:  # Large spending alert
            alerts.append(f"Alert: High spending on {row['date']} of {row['amount']}")
    return alerts

#-------------------------------------------------------------------------------------------------------------------
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def get_top_time_intervals(credit_df, debit_df):
    try:
        all_transactions = pd.concat([credit_df, debit_df], ignore_index=True)
        all_transactions['time'] = all_transactions['date'].dt.hour
        time_counts = all_transactions.groupby('time').size().reset_index(name='transaction_count')
        time_counts['time'] = time_counts['time'].apply(lambda x: f"{x:02d}:00")
        result = time_counts.sort_values(by='transaction_count', ascending=False).head(3)
        print("Time intervals data:", result.to_dict('records'))  # Debug print
        return result
    except Exception as e:
        print("Error in get_top_time_intervals:", e)
        return pd.DataFrame()
